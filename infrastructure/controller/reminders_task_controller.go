package infrastructure

//TODO: hardening https://chatgpt.com/c/6818a8ec-47e4-800c-8c06-33b4672f7467

import (
	"encoding/json"
	"errors"
	"fmt"
	"lazytask/entities"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"strconv"
	"time"
)

// Types from reminders-cli -------------------------------------------------------------

type ReminderList = string

type Reminder struct {
	CreationDate time.Time `json:"creationDate"`
	DueDate      time.Time `json:"dueDate"`
	ExternalID   string    `json:"externalId"`
	IsCompleted  bool      `json:"isCompleted"`
	LastModified time.Time `json:"lastModified"`
	// The list id
	List     ReminderList `json:"list"`
	Notes    string       `json:"notes"`
	Priority int          `json:"priority"`
	Title    string       `json:"title"`
}

type Reminders []Reminder

// Conversion methods ------------------------------------------------------------------

func (r Reminder) ToTask() entities.Task {
	return entities.Task{
		DueDate:     r.DueDate,
		Id:          r.ExternalID,
		IsCompleted: r.IsCompleted,
		ListId:      r.List,
		Description: r.Notes,
		Priority:    r.Priority,
		Title:       r.Title,
	}
}

func (reminders Reminders) ToTasks() []entities.Task {
	tasks := []entities.Task{}
	for _, reminder := range reminders {
		tasks = append(tasks, reminder.ToTask())
	}

	return tasks
}

func ToReminder(t entities.Task) Reminder {
	return Reminder{
		DueDate:     t.DueDate,
		ExternalID:  t.Id,
		IsCompleted: t.IsCompleted,
		List:        ReminderList(t.ListId),
		Notes:       t.Description,
		Priority:    t.Priority,
		Title:       t.Title,
	}
}

func ToList(r ReminderList) entities.List {
	return entities.List{
		Id: string(r),
		// Since the reminder list is just a string, the entities.List will have the same
		// values for id and title. We are using the name as an ID for now.
		Title: string(r),
	}
}

func ToLists(rl []ReminderList) []entities.List {
	lists := []entities.List{}
	for _, reminderList := range rl {
		lists = append(lists, ToList(reminderList))
	}

	return lists
}

func ToReminderList(l entities.List) ReminderList {
	return ReminderList(l.Id)
}

// Functions ----------------------------------------------------------------------

// This function tries to find the project root by looking for go.mod or .git
func findProjectRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}

	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir, nil
		}

		if _, err := os.Stat(filepath.Join(dir, ".git")); err == nil {
			return dir, nil
		}

		parentDir := filepath.Dir(dir)
		if parentDir == dir {
			break // We've reached the root directory
		}
		dir = parentDir
	}

	return "", fmt.Errorf("Project root not found")
}

// returns the path to the reminders executable
func getExecutablePath() (string, error) {
	root, err := findProjectRoot()
	if err != nil {
		return "", err
	}
	return filepath.Join(root, "adapters/reminders-cli/reminders"), nil
}

func parseJson[T any](output []byte) (T, error) {
	var result T
	err := json.Unmarshal(output, &result)
	if err != nil {
		return *new(T), fmt.Errorf("Failed to parse JSON: %w", err)
	}

	return result, err
}

// Runs an external command and discards the output
func execCommandWithoutOutput(commandArgs []string) error {
	execPath, execPathErr := getExecutablePath()
	if execPathErr != nil {
		return execPathErr
	}

	// Run the command
	log.Printf("Executing command: %s %v", execPath, commandArgs)
	cmd := exec.Command(execPath, commandArgs...)

	// Capture both stdout and stderr
	output, err := cmd.CombinedOutput()

	// Log output for debugging
	// if len(output) > 0 {
	// 	// log.printf("Command output: %s", string(output))
	// }

	if err != nil {
		return fmt.Errorf("Command failed: %s - Error: %v", string(output), err)
	}

	return nil
}

// execCommand runs an external command and parses the JSON result
func execCommand[T any](commandArgs []string) (T, error) {
	// Add JSON format flag for response
	commandArgs = append(commandArgs, "--format", "json")

	execPath, execPathErr := getExecutablePath()
	if execPathErr != nil {
		return *new(T), execPathErr
	}

	// Run the command
	log.Printf("Executing JSON command: %s %v", execPath, commandArgs)
	cmd := exec.Command(execPath, commandArgs...)

	// Capture both stdout and stderr
	output, err := cmd.CombinedOutput()

	// // Log output for debugging
	// if len(output) > 0 {
	// 	// For JSON responses, only log the first 500 chars to avoid huge logs
	// 	outputToLog := string(output)
	// 	if len(outputToLog) > 500 {
	// 		outputToLog = outputToLog[:500] + "... [truncated]"
	// 	}
	// 	// log.printf("JSON command output: %s", outputToLog)
	// }

	if err != nil {
		return *new(T), fmt.Errorf("JSON command failed: %s - Error: %v", string(output), err)
	}

	// Try to parse the JSON
	result, err := parseJson[T](output)
	if err != nil {
		return *new(T), err
	}
	return result, nil
}

func getListAndIndexForCompletion(taskId string) (ReminderList, int, error) {
	allReminders, err := execCommand[Reminders]([]string{"show-all"})
	if err != nil {
		return "Not found", -1, fmt.Errorf("Failed to get all tasks: %w", err)
	}

	allRemindersCompletionIndex := slices.IndexFunc(allReminders, func(r Reminder) bool {
		return r.ExternalID == taskId
	})

	if allRemindersCompletionIndex == -1 {
		return "Not found", -1, errors.New("Task not found")
	}

	listToCompleteOn := allReminders[allRemindersCompletionIndex].List

	listReminders, listErr := execCommand[Reminders]([]string{"show", listToCompleteOn})
	if listErr != nil {
		return "Not found", -1, fmt.Errorf("Failed to get tasks of list %s: %w", listToCompleteOn, listErr)
	}

	reminderToCompleteListIndex := slices.IndexFunc(listReminders, func(r Reminder) bool {
		return r.ExternalID == taskId
	})

	if reminderToCompleteListIndex == -1 {
		return "Not found.", -1, errors.New("Task not found on specific list.")
	}

	return listToCompleteOn, reminderToCompleteListIndex, nil
}

// Controller --------------------------------------------------------------------

type ReminderTaskController struct{}

func NewReminderTaskController() *ReminderTaskController {
	log.Printf("Apple Reminders controller initialized.")
	return &ReminderTaskController{}
}

// GetLists retrieves all task lists
func (r ReminderTaskController) GetLists() ([]entities.List, error) {
	reminderLists, err := execCommand[[]ReminderList]([]string{"show-lists"})
	if err != nil {
		return []entities.List{}, err
	}

	return ToLists(reminderLists), nil
}

func (r ReminderTaskController) GetListById(listId string) (entities.List, error) {
	lists, err := r.GetLists()
	if err != nil {
		return entities.List{}, err
	}

	listIndex := slices.IndexFunc(lists, func(rl entities.List) bool {
		return rl.Id == listId
	})

	if listIndex == -1 {
		return entities.List{}, errors.New("List not found through controller.")
	}

	return lists[listIndex], nil
}

func (r ReminderTaskController) GetTaskById(taskId string) (entities.Task, error) {
	// TODO: when fetching these i need to make sure to handle errors. I cant cache this.
	// TODO all of these should handle errors and return nil or empty
	return entities.Task{}, errors.New("Not implemented")
}

func (r ReminderTaskController) GetTasksByList(listId string) ([]entities.Task, error) {
	// TODO: reminders-cli can't handle lists with multiple workds yet
	// return execCommand[[]do.Task]([]string{"show", "'" + listId + "'"})
	// reminders, err := execCommand[Reminders]([]string{"show", "\"" + listId + "\""})
	reminders, err := execCommand[Reminders]([]string{"show", listId})
	if err != nil {
		// LogError("Failed to get tasks for list: %s", err)
		return []entities.Task{}, fmt.Errorf("failed to get tasks for list: %w", err)
	}

	return reminders.ToTasks(), nil
}

// AddTask adds a new task
func (r ReminderTaskController) AddTask(t entities.Task) error {
	reminder := ToReminder(t)

	// commandString := []string{"add", reminder.List, "\"" + reminder.Title + "\""}
	// TODO: unclear if it can handle multiple words
	commandString := []string{"add", reminder.List, "" + reminder.Title + ""}

	if reminder.Notes != "" {
		commandString = append(commandString, "--notes", "\""+reminder.Notes+"\"")
	}
	if reminder.DueDate != (time.Time{}) {
		commandString = append(commandString, "--due-date", reminder.DueDate.Format("2006-01-02"))
	}

	if reminder.Priority != 0 {
		prioString := "none"
		if reminder.Priority == 1 {
			prioString = "high"
		} else if reminder.Priority > 1 {
			prioString = "medium"
		} else if reminder.Priority > 5 {
			prioString = "low"
		}
		commandString = append(commandString, "--priority", prioString)
	}

	_, err := execCommand[Reminder](commandString)
	if err != nil {
		return fmt.Errorf("failed to add task: %w", err)
	}

	return nil
}

// CompleteTask marks a task as completed
func (r ReminderTaskController) CompleteTask(taskId string) error {
	listName, reminderIndex, err := getListAndIndexForCompletion(taskId)
	if err != nil {
		// LogError("Failed to get list and index for completion: %s", err)
	}

	err = execCommandWithoutOutput([]string{"complete", listName, strconv.Itoa(reminderIndex)})

	if err != nil {
		// LogError("Failed to complete task: %s", err)
		return fmt.Errorf("failed to complete task: %w", err)
	}

	return nil
}

// UncompleteTask marks a task as uncompleted
func (r ReminderTaskController) UncompleteTask(taskId string) error {
	reminders, err := execCommand[Reminders]([]string{"show-all", "--only-completed"})
	if err != nil {
		// LogError("Failed to get completed tasks: %s", err)
	}

	reminderToUncompleteIndex := slices.IndexFunc(reminders, func(r Reminder) bool {
		return r.ExternalID == taskId
	})

	if reminderToUncompleteIndex == -1 {
		return errors.New("Task not found")
	}

	reminderToUncompleteList := reminders[reminderToUncompleteIndex].List

	_, err = execCommand[any]([]string{"uncomplete", "\"" + reminderToUncompleteList + "\"", strconv.Itoa(reminderToUncompleteIndex)})

	if err != nil {
		return fmt.Errorf("failed to uncomplete task: %w", err)
	}

	return nil
}

// Update a task
func (r ReminderTaskController) UpdateTask(task entities.Task) error {
	// // log.printf("UpdateTask: Starting update for task ID: %s", task.Id)
	// // log.printf("UpdateTask: Task details - Title: %s, DueDate: %s", task.Title, task.DueDate)

	// Find the correct list and index for the task
	listName, reminderIndex, err := getListAndIndexForCompletion(task.Id)
	if err != nil {
		// LogError("UpdateTask: Failed to find task for update: %s", err)
		return fmt.Errorf("failed to find task for update: %w", err)
	}

	// // log.printf("UpdateTask: Found task at list: %s, index: %d", listName, reminderIndex)

	// Convert domain task to Reminder
	// reminder := ReminderFromTask(task)

	// Using a simpler approach - delete and recreate instead of trying to edit
	// This is more reliable given the CLI.swift limitations

	// First, get the current task to preserve all properties
	// log.printf("UpdateTask: Fetching current task to preserve properties")
	currentTasks, tListErr := r.GetTasksByList(listName)
	if tListErr != nil {
		return tListErr
	}
	var currentTask entities.Task
	found := false

	for _, t := range currentTasks {
		if t.Id == task.Id {
			currentTask = t
			found = true
			// // log.printf("UpdateTask: Found current task: %+v", currentTask)
			break
		}
	}

	if !found {
		// LogError("UpdateTask: ERROR - Task not found in current tasks")
		return fmt.Errorf("task not found for update")
	}

	// Delete the current task
	// // log.printf("UpdateTask: Deleting task at index %d from list %s", reminderIndex, listName)
	deleteArgs := []string{"delete", listName, strconv.Itoa(reminderIndex)}
	// // log.printf("UpdateTask: Delete command: %v", deleteArgs)

	err = execCommandWithoutOutput(deleteArgs)
	if err != nil {
		// LogError("UpdateTask: Failed to delete task: %s", err)
		return fmt.Errorf("failed to delete task for update: %w", err)
	}

	// Create a new task with the updated properties
	// Start with title from the current task, but use updated properties where provided
	title := currentTask.Title
	if task.Title != "" {
		title = task.Title
	}

	// Create the add command
	addArgs := []string{"add", listName, title}
	// // log.printf("UpdateTask: Creating new task with title: %s", title)

	// Add notes
	description := currentTask.Description
	if task.Description != "" {
		description = task.Description
	}
	if description != "" {
		addArgs = append(addArgs, "--notes", description)
		// // log.printf("UpdateTask: Adding notes: %s", description)
	}

	// Add the due date (either the new one or preserve the old one)
	dueDate := currentTask.DueDate
	if !task.DueDate.IsZero() {
		dueDate = task.DueDate
	}
	if !dueDate.IsZero() {
		dateString := dueDate.Format("2006-01-02")
		addArgs = append(addArgs, "--due-date", dateString)
		// // log.printf("UpdateTask: Setting due date: %s", dateString)
	}

	// Add priority
	priority := currentTask.Priority
	if task.Priority != 0 {
		priority = task.Priority
	}
	if priority != 0 {
		prioString := "none"
		if priority == 1 {
			prioString = "high"
		} else if priority > 1 {
			prioString = "medium"
		} else if priority > 5 {
			prioString = "low"
		}
		addArgs = append(addArgs, "--priority", prioString)
		// // log.printf("UpdateTask: Setting priority: %s", prioString)
	}

	// Log the full command we're about to execute
	// // log.printf("UpdateTask: Running add command: %v", addArgs)

	// Execute the add command to recreate the task
	_, err = execCommand[Reminder](addArgs)
	if err != nil {
		// LogError("UpdateTask: Failed to recreate task: %s", err)
		return fmt.Errorf("failed to recreate task: %w", err)
	}

	// // log.printf("UpdateTask: Task successfully updated")
	return nil
}

// MoveTaskToList moves a task to a different list
func (r ReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {
	return errors.New("Not implemented")
	// TODO:
	// _, err := execCommand[any]([]string{"move-task", "--task-id", taskId, "--list-id", targetListId})
	// if err != nil {
	// 	return fmt.Errorf("failed to move task: %w", err)
	// }

	// return nil
}
