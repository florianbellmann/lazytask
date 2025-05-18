package infrastructure

import (
	"encoding/json"
	"errors"
	"fmt"
	"lazytask/entities"
	"log"
	"os"
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

func (r Reminder) toTask() entities.Task {
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

func (reminders Reminders) toTasks() []entities.Task {
	tasks := []entities.Task{}
	for _, reminder := range reminders {
		tasks = append(tasks, reminder.toTask())
	}

	return tasks
}

func toReminder(t entities.Task) Reminder {
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

func toList(r ReminderList) entities.List {
	return entities.List{
		Id: string(r),
		// Since the reminder list is just a string, the entities.List will have the same
		// values for id and title. We are using the name as an ID for now.
		Title: string(r),
	}
}

func toLists(rl []ReminderList) []entities.List {
	lists := []entities.List{}
	for _, reminderList := range rl {
		lists = append(lists, toList(reminderList))
	}

	return lists
}

func toReminderList(l entities.List) ReminderList {
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

// getListAndIndexForCompletion retrieves the list and index of a task to be completed
// It first finds the task in the list of all reminders, then finds the task in the specific list
// It returns the list name and the index of the task in that list
// If the task is not found, it returns an error
func getListAndIndexForCompletion(allReminders Reminders, taskId string) (ReminderList, int, error) {
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

func parseJson[T any](output []byte) (T, error) {
	var result T
	err := json.Unmarshal(output, &result)
	if err != nil {
		return *new(T), fmt.Errorf("Failed to parse JSON: %w", err)
	}

	return result, err
}

// Controller --------------------------------------------------------------------

type ReminderTaskController struct {
	cmd Commander
}

func NewReminderTaskController(cmd Commander) *ReminderTaskController {
	log.Printf("Apple Reminders controller initialized.")
	return &ReminderTaskController{
		cmd: cmd,
	}
}

// GetLists retrieves all task lists
func (r ReminderTaskController) GetLists() ([]entities.List, error) {
	stdOut, err := r.cmd.Exec([]string{"show-lists"})
	if err != nil {
		return []entities.List{}, err
	}

	reminderLists, err := parseJson[[]ReminderList](stdOut)
	if err != nil {
		return []entities.List{}, err
	}

	return toLists(reminderLists), nil
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
	stdOut, err := r.cmd.Exec([]string{"show", listId})
	if err != nil {
		return []entities.Task{}, err
	}
	reminders, err := parseJson[Reminders](stdOut)
	if err != nil {
		return []entities.Task{}, err
	}

	return reminders.toTasks(), nil
}

// AddTask adds a new task
func (r ReminderTaskController) AddTask(t entities.Task) error {
	reminder := toReminder(t)

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

	_, err := r.cmd.Exec(commandString)
	if err != nil {
		return fmt.Errorf("failed to add task: %w", err)
	}

	return nil
}

// CompleteTask marks a task as completed
func (r ReminderTaskController) CompleteTask(taskId string) error {
	stdOut, err := r.cmd.Exec([]string{"show-all"}) // TODO: move these magic strings to the commander
	if err != nil {
		return err
	}
	allReminders, err := parseJson[Reminders](stdOut)
	if err != nil {
		return err
	}

	listName, reminderIndex, err := getListAndIndexForCompletion(allReminders, taskId)
	if err != nil {
		return err
	}

	err = r.cmd.ExecWithoutOutput([]string{"complete", listName, strconv.Itoa(reminderIndex)})

	if err != nil {
		return err
	}

	return nil
}

// UncompleteTask marks a task as uncompleted
func (r ReminderTaskController) UncompleteTask(taskId string) error {
	stdOut, err := r.cmd.Exec([]string{"show-all", "--only-completed"})
	if err != nil {
		return err
	}
	reminders, err := parseJson[Reminders](stdOut)
	if err != nil {
		return err
	}

	reminderToUncompleteIndex := slices.IndexFunc(reminders, func(r Reminder) bool {
		return r.ExternalID == taskId
	})

	if reminderToUncompleteIndex == -1 {
		return errors.New("Task not found")
	}

	reminderToUncompleteList := reminders[reminderToUncompleteIndex].List

	_, err = r.cmd.Exec([]string{"uncomplete", "\"" + reminderToUncompleteList + "\"", strconv.Itoa(reminderToUncompleteIndex)})

	if err != nil {
		return err
	}

	return nil
}

// Update a task
func (r ReminderTaskController) UpdateTask(task entities.Task) error {
	// // log.printf("UpdateTask: Starting update for task ID: %s", task.Id)
	// // log.printf("UpdateTask: Task details - Title: %s, DueDate: %s", task.Title, task.DueDate)

	stdOut, err := r.cmd.Exec([]string{"show-all"}) // TODO: move these magic strings to the commander
	if err != nil {
		return err
	}
	allReminders, err := parseJson[Reminders](stdOut)
	if err != nil {
		return err
	}

	// Find the correct list and index for the task
	listName, reminderIndex, err := getListAndIndexForCompletion(allReminders, task.Id)
	if err != nil {
		return err
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

	err = r.cmd.ExecWithoutOutput(deleteArgs)
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
	_, err = r.cmd.Exec(addArgs)
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
