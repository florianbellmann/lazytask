package infrastructure

import (
	// "errors"
	// "fmt"
	"lazytask/entities"
	"reflect"
	"testing"
	"time"
)

type dummyCommander struct {
	lastArgs []string
	response []byte
	err      error
}

func (d *dummyCommander) Exec(args []string) ([]byte, error) {
	d.lastArgs = args
	return d.response, d.err
}

func (d *dummyCommander) ExecWithoutOutput(args []string) error {
	d.lastArgs = args
	return d.err
}

func TestGetLists(t *testing.T) {
	// Test GetLists
	dummy := &dummyCommander{response: []byte(`["l1","l2"]`)}
	ctrl := &ReminderTaskController{
		cmd: &dummyCommander{},
	}
	lists, err := ctrl.GetLists()
	if err != nil {
		t.Fatalf("GetLists() error: %v", err)
	}
	if len(lists) != 2 || lists[0].Id != "l1" || lists[1].Id != "l2" {
		t.Errorf("GetLists() = %v, want l1,l2", lists)
	}
	if !reflect.DeepEqual(dummy.lastArgs, []string{"show-lists"}) {
		t.Errorf("GetLists() exec args = %v, want [\"show-lists\"]", dummy.lastArgs)
	}
}

func TestGetListById(t *testing.T) {
	// dummy := &dummyCommander{response: []byte(`["l1","l2"]`)}
	ctrl := &ReminderTaskController{
		cmd: &dummyCommander{},
	}

	// Test GetListById success
	list, err := ctrl.GetListById("l2")
	if err != nil || list.Id != "l2" {
		t.Errorf("GetListById() = %v, %v, want Id l2", list, err)
	}
	// Test GetListById not found
	if _, err := ctrl.GetListById("nope"); err == nil {
		t.Error("GetListById() expected error for missing id, got nil")
	}
}

// ----
// https://chatgpt.com/c/6829bf06-1318-800c-81b5-e329470e948b

// this way i can test the reminders controller fully
// only the commander cant be tested other than with real tests
// for the rest i spoof it
//
// 	in reminder tests i spoof it
//
//
// 	in bubble tea tests, i spoof the app service and it wont have a reminders controller, only in memory repo

// // Original execCommand and execCommandWithoutOutput functions
// var originalExecCommand = execCommand
// var originalExecCommandWithoutOutput = execCommandWithoutOutput
//
// // MockExecutor allows us to mock the CLI commands that would normally be executed
// type MockExecutor struct {
// 	// Track calls to commands for verification
// 	CommandCalls     [][]string
// 	MockLists        []ReminderList
// 	MockReminders    Reminders
// 	MockReminderById Reminder
// 	ShouldFail       bool
// }
//
// // Mock instance that will be used across tests
// var mockExecutor = &MockExecutor{
// 	CommandCalls: [][]string{},
// 	ShouldFail:   false,
// }
//
// // Setup initializes the mock executor with test data
// func setupMockExecutor() {
// 	currentTime := time.Now()
//
// 	// Create mock data
// 	mockLists := []ReminderList{"List1", "List2"}
// 	mockReminders := Reminders{
// 		{
// 			CreationDate: currentTime.Add(-48 * time.Hour),
// 			DueDate:      currentTime.Add(24 * time.Hour),
// 			ExternalID:   "task1",
// 			IsCompleted:  false,
// 			LastModified: currentTime.Add(-24 * time.Hour),
// 			List:         "List1",
// 			Notes:        "Task 1 notes",
// 			Priority:     1,
// 			Title:        "Task 1",
// 		},
// 		{
// 			CreationDate: currentTime.Add(-24 * time.Hour),
// 			DueDate:      currentTime.Add(48 * time.Hour),
// 			ExternalID:   "task2",
// 			IsCompleted:  false,
// 			LastModified: currentTime,
// 			List:         "List1",
// 			Notes:        "Task 2 notes",
// 			Priority:     2,
// 			Title:        "Task 2",
// 		},
// 		{
// 			CreationDate: currentTime.Add(-12 * time.Hour),
// 			DueDate:      currentTime.Add(72 * time.Hour),
// 			ExternalID:   "task3",
// 			IsCompleted:  true,
// 			LastModified: currentTime,
// 			List:         "List2",
// 			Notes:        "Task 3 notes",
// 			Priority:     5,
// 			Title:        "Task 3",
// 		},
// 	}
//
// 	mockExecutor.MockLists = mockLists
// 	mockExecutor.MockReminders = mockReminders
// 	mockExecutor.CommandCalls = [][]string{}
// 	mockExecutor.ShouldFail = false
// }
//
// // Mock implementation of execCommand
// func mockExecCommandFunc[T any](commandArgs []string) (T, error) {
// 	// Record the call
// 	mockExecutor.CommandCalls = append(mockExecutor.CommandCalls, commandArgs)
//
// 	// Check if we should simulate failure
// 	if mockExecutor.ShouldFail {
// 		return *new(T), errors.New("mock executor error")
// 	}
//
// 	// Return appropriate mock data based on the command
// 	if len(commandArgs) > 0 {
// 		command := commandArgs[0]
// 		switch command {
// 		case "show-lists":
// 			if result, ok := any(mockExecutor.MockLists).(T); ok {
// 				return result, nil
// 			}
// 		case "show-all":
// 			if result, ok := any(mockExecutor.MockReminders).(T); ok {
// 				return result, nil
// 			}
// 		case "show":
// 			if len(commandArgs) > 1 {
// 				listName := commandArgs[1]
// 				// Filter reminders that belong to the requested list
// 				filteredReminders := Reminders{}
// 				for _, reminder := range mockExecutor.MockReminders {
// 					if string(reminder.List) == listName {
// 						filteredReminders = append(filteredReminders, reminder)
// 					}
// 				}
// 				if result, ok := any(filteredReminders).(T); ok {
// 					return result, nil
// 				}
// 			}
// 		case "add":
// 			// Mock adding a reminder and return it
// 			newReminder := Reminder{
// 				ExternalID:   "new-mock-id",
// 				Title:        commandArgs[2],
// 				List:         ReminderList(commandArgs[1]),
// 				CreationDate: time.Now(),
// 				LastModified: time.Now(),
// 			}
//
// 			// Process additional args
// 			for i := 3; i < len(commandArgs); i += 2 {
// 				if i+1 < len(commandArgs) {
// 					flag := commandArgs[i]
// 					value := commandArgs[i+1]
//
// 					switch flag {
// 					case "--notes":
// 						newReminder.Notes = value
// 					case "--priority":
// 						switch value {
// 						case "high":
// 							newReminder.Priority = 1
// 						case "medium":
// 							newReminder.Priority = 2
// 						case "low":
// 							newReminder.Priority = 5
// 						}
// 					case "--due-date":
// 						// Simple date parsing - in a real implementation would need more robust handling
// 						dueDate, _ := time.Parse("2006-01-02", value)
// 						newReminder.DueDate = dueDate
// 					}
// 				}
// 			}
//
// 			// Add to mock reminders
// 			mockExecutor.MockReminders = append(mockExecutor.MockReminders, newReminder)
// 			if result, ok := any(newReminder).(T); ok {
// 				return result, nil
// 			}
// 		}
// 	}
//
// 	// Default fallback
// 	return *new(T), nil
// }
//
// // Mock implementation of execCommandWithoutOutput
// func mockExecCommandWithoutOutputFunc(commandArgs []string) error {
// 	// Record the call
// 	mockExecutor.CommandCalls = append(mockExecutor.CommandCalls, commandArgs)
//
// 	// Check if we should simulate failure
// 	if mockExecutor.ShouldFail {
// 		return errors.New("mock executor error")
// 	}
//
// 	// Handle complete/uncomplete/delete commands
// 	if len(commandArgs) > 0 {
// 		command := commandArgs[0]
// 		switch command {
// 		case "complete":
// 			// Mark the task as completed
// 			if len(commandArgs) > 2 {
// 				listName := commandArgs[1]
// 				// In a real implementation, would use the index to find the task
// 				// For mock, we'll just mark tasks in that list as completed
// 				for i := range mockExecutor.MockReminders {
// 					if mockExecutor.MockReminders[i].List == ReminderList(listName) {
// 						mockExecutor.MockReminders[i].IsCompleted = true
// 						break
// 					}
// 				}
// 			}
// 		case "uncomplete":
// 			// Mark the task as not completed
// 			if len(commandArgs) > 2 {
// 				listName := commandArgs[1]
// 				// For mock, we'll just mark tasks in that list as not completed
// 				for i := range mockExecutor.MockReminders {
// 					if mockExecutor.MockReminders[i].List == ReminderList(listName) {
// 						mockExecutor.MockReminders[i].IsCompleted = false
// 						break
// 					}
// 				}
// 			}
// 		case "delete":
// 			// Remove a task
// 			if len(commandArgs) > 2 {
// 				listName := commandArgs[1]
// 				// Simple mock deletion - in real implementation would use the index
// 				for i := range mockExecutor.MockReminders {
// 					if mockExecutor.MockReminders[i].List == ReminderList(listName) {
// 						// Remove this reminder from the slice
// 						mockExecutor.MockReminders = append(mockExecutor.MockReminders[:i], mockExecutor.MockReminders[i+1:]...)
// 						break
// 					}
// 				}
// 			}
// 		}
// 	}
//
// 	return nil
// }
//
// // Helper function to patch in our mock functions
// func patchExecFunctions() {
// 	execCommand = mockExecCommandFunc
// 	execCommandWithoutOutput = mockExecCommandWithoutOutputFunc
// }
//
// // Helper function to restore the original functions
// func restoreExecFunctions() {
// 	execCommand = originalExecCommand
// 	execCommandWithoutOutput = originalExecCommandWithoutOutput
// }
//
// // Setup/teardown for each test
// func setupTest() {
// 	setupMockExecutor()
// 	patchExecFunctions()
// }
//
// func teardownTest() {
// 	restoreExecFunctions()
// }
//
// // Tests start here
//
// // TestNewReminderTaskController tests the creation of a new controller
// func TestNewReminderTaskController(t *testing.T) {
// 	// No need to patch for this test
// 	controller := NewReminderTaskController()
//
// 	if controller == nil {
// 		t.Error("NewReminderTaskController returned nil")
// 	}
// }
//
// // TestGetLists tests retrieving all lists
// func TestGetLists(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
// 	lists, err := controller.GetLists()
//
// 	if err != nil {
// 		t.Errorf("GetLists returned an error: %v", err)
// 	}
//
// 	if len(lists) != 2 {
// 		t.Errorf("Expected 2 lists, got %d", len(lists))
// 	}
//
// 	// Check command was called correctly
// 	if len(mockExecutor.CommandCalls) != 1 {
// 		t.Error("Expected one command call")
// 	} else if mockExecutor.CommandCalls[0][0] != "show-lists" {
// 		t.Errorf("Expected 'show-lists' command, got %s", mockExecutor.CommandCalls[0][0])
// 	}
//
// 	// Test error case
// 	mockExecutor.ShouldFail = true
// 	_, err = controller.GetLists()
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestGetListById tests retrieving a list by ID
// func TestGetListById(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// Test existing list
// 	list, err := controller.GetListById("List1")
// 	if err != nil {
// 		t.Errorf("GetListById returned error for existing list: %v", err)
// 	}
// 	if list.Id != "List1" || list.Title != "List1" {
// 		t.Errorf("GetListById returned incorrect list. Expected: {List1, List1}, Got: {%s, %s}",
// 			list.Id, list.Title)
// 	}
//
// 	// Test non-existent list
// 	_, err = controller.GetListById("NonExistentList")
// 	if err == nil {
// 		t.Error("GetListById did not return error for non-existent list")
// 	}
//
// 	// Test error case from GetLists
// 	mockExecutor.ShouldFail = true
// 	_, err = controller.GetListById("List1")
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestGetTasksByList tests retrieving tasks by list ID
// func TestGetTasksByList(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// Test list with multiple tasks
// 	listTasks, err := controller.GetTasksByList("List1")
// 	if err != nil {
// 		t.Errorf("GetTasksByList returned error: %v", err)
// 	}
// 	if len(listTasks) != 2 {
// 		t.Errorf("Expected 2 tasks for List1, got %d", len(listTasks))
// 	}
//
// 	// Check command was called correctly
// 	if len(mockExecutor.CommandCalls) != 1 {
// 		t.Error("Expected one command call")
// 	} else if mockExecutor.CommandCalls[0][0] != "show" || mockExecutor.CommandCalls[0][1] != "List1" {
// 		t.Errorf("Expected 'show List1' command, got %v", mockExecutor.CommandCalls[0])
// 	}
//
// 	// Test list with one task
// 	mockExecutor.CommandCalls = [][]string{} // Reset calls
// 	listTasks, err = controller.GetTasksByList("List2")
// 	if err != nil {
// 		t.Errorf("GetTasksByList returned error: %v", err)
// 	}
// 	if len(listTasks) != 1 {
// 		t.Errorf("Expected 1 task for List2, got %d", len(listTasks))
// 	}
//
// 	// Test error case
// 	mockExecutor.ShouldFail = true
// 	_, err = controller.GetTasksByList("List1")
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestAddTask tests adding a task
// func TestAddTask(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// Test adding task to existing list
// 	task := entities.Task{
// 		Id:          "task4",
// 		Title:       "Task 4",
// 		ListId:      "List1",
// 		Description: "Task 4 description",
// 		DueDate:     time.Now().Add(24 * time.Hour),
// 		Priority:    1,
// 	}
//
// 	initialRemindersCount := len(mockExecutor.MockReminders)
//
// 	err := controller.AddTask(task)
// 	if err != nil {
// 		t.Errorf("AddTask returned error: %v", err)
// 	}
//
// 	// Verify command was called correctly
// 	if len(mockExecutor.CommandCalls) != 1 {
// 		t.Error("Expected one command call")
// 	} else if mockExecutor.CommandCalls[0][0] != "add" ||
// 		mockExecutor.CommandCalls[0][1] != "List1" ||
// 		mockExecutor.CommandCalls[0][2] != "Task 4" {
// 		t.Errorf("Expected 'add List1 Task 4' command, got %v", mockExecutor.CommandCalls[0])
// 	}
//
// 	// Verify a new reminder was added to the mock
// 	if len(mockExecutor.MockReminders) != initialRemindersCount+1 {
// 		t.Errorf("Expected %d reminders, got %d", initialRemindersCount+1, len(mockExecutor.MockReminders))
// 	}
//
// 	// Test error case
// 	mockExecutor.ShouldFail = true
// 	err = controller.AddTask(task)
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestCompleteTask tests completing a task
// func TestCompleteTask(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// We need to make sure getListAndIndexForCompletion can find the task
// 	// So we need to set up the mock data for the "show-all" command first
//
// 	// Test completing existing task
// 	err := controller.CompleteTask("task1")
// 	if err != nil {
// 		t.Errorf("CompleteTask returned error: %v", err)
// 	}
//
// 	// Verify command sequence for getListAndIndexForCompletion followed by complete
// 	found := false
// 	completeFound := false
//
// 	for _, call := range mockExecutor.CommandCalls {
// 		if len(call) > 0 {
// 			if call[0] == "show-all" {
// 				found = true
// 			} else if call[0] == "complete" && call[1] == "List1" {
// 				completeFound = true
// 			}
// 		}
// 	}
//
// 	if !found {
// 		t.Error("Expected 'show-all' command not found")
// 	}
//
// 	if !completeFound {
// 		t.Error("Expected 'complete List1 index' command not found")
// 	}
//
// 	// Test error case
// 	mockExecutor.ShouldFail = true
// 	err = controller.CompleteTask("task2")
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestUncompleteTask tests uncompleting a task
// func TestUncompleteTask(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// First, make sure we have a completed task
// 	for i, reminder := range mockExecutor.MockReminders {
// 		if reminder.ExternalID == "task3" {
// 			mockExecutor.MockReminders[i].IsCompleted = true
// 			break
// 		}
// 	}
//
// 	// Reset command calls
// 	mockExecutor.CommandCalls = [][]string{}
//
// 	// Test uncompleting existing task
// 	err := controller.UncompleteTask("task3")
// 	if err != nil {
// 		t.Errorf("UncompleteTask returned error: %v", err)
// 	}
//
// 	// Verify command was called correctly
// 	showAllFound := false
// 	uncompleteFound := false
//
// 	for _, call := range mockExecutor.CommandCalls {
// 		if len(call) > 0 {
// 			if call[0] == "show-all" && slicesContains(call, "--only-completed") {
// 				showAllFound = true
// 			} else if call[0] == "uncomplete" {
// 				uncompleteFound = true
// 			}
// 		}
// 	}
//
// 	if !showAllFound {
// 		t.Error("Expected 'show-all --only-completed' command not found")
// 	}
//
// 	if !uncompleteFound {
// 		t.Error("Expected 'uncomplete' command not found")
// 	}
//
// 	// Test error case
// 	mockExecutor.ShouldFail = true
// 	err = controller.UncompleteTask("task3")
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestUpdateTask tests updating a task
// func TestUpdateTask(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// Test updating existing task
// 	updatedTask := entities.Task{
// 		Id:          "task1",
// 		Title:       "Updated Task 1",
// 		ListId:      "List1",
// 		Description: "Updated description",
// 		DueDate:     time.Now().Add(48 * time.Hour),
// 		Priority:    2,
// 	}
//
// 	err := controller.UpdateTask(updatedTask)
// 	if err != nil {
// 		t.Errorf("UpdateTask returned error: %v", err)
// 	}
//
// 	// Verify commands were called correctly
// 	getListAndIndexFound := false
// 	deleteCommand := false
// 	addCommand := false
//
// 	for _, call := range mockExecutor.CommandCalls {
// 		if len(call) > 0 {
// 			if call[0] == "show-all" {
// 				getListAndIndexFound = true
// 			} else if call[0] == "delete" && call[1] == "List1" {
// 				deleteCommand = true
// 			} else if call[0] == "add" && call[1] == "List1" && call[2] == "Updated Task 1" {
// 				addCommand = true
// 				// Check for presence of flags
// 				notesFound := false
// 				priorityFound := false
// 				dueDateFound := false
//
// 				for i := 3; i < len(call); i++ {
// 					if call[i] == "--notes" {
// 						notesFound = true
// 					} else if call[i] == "--priority" {
// 						priorityFound = true
// 					} else if call[i] == "--due-date" {
// 						dueDateFound = true
// 					}
// 				}
//
// 				if !notesFound {
// 					t.Error("Notes flag not found in add command")
// 				}
// 				if !priorityFound {
// 					t.Error("Priority flag not found in add command")
// 				}
// 				if !dueDateFound {
// 					t.Error("Due date flag not found in add command")
// 				}
// 			}
// 		}
// 	}
//
// 	if !getListAndIndexFound {
// 		t.Error("Expected call to get list and index not found")
// 	}
//
// 	if !deleteCommand {
// 		t.Error("Delete command not found")
// 	}
//
// 	if !addCommand {
// 		t.Error("Add command not found")
// 	}
//
// 	// Test error case
// 	mockExecutor.ShouldFail = true
// 	err = controller.UpdateTask(updatedTask)
// 	if err == nil {
// 		t.Error("Expected error when executor fails, got nil")
// 	}
// }
//
// // TestMoveTaskToList tests moving a task to another list
// // This feature is not implemented in the controller, so we just test it returns "not implemented"
// func TestMoveTaskToList(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	err := controller.MoveTaskToList("task1", "List2")
// 	if err == nil || err.Error() != "Not implemented" {
// 		t.Errorf("Expected 'Not implemented' error, got: %v", err)
// 	}
// }
//
// // TestGetTaskById tests retrieving a task by ID
// func TestGetTaskById(t *testing.T) {
// 	setupTest()
// 	defer teardownTest()
//
// 	controller := NewReminderTaskController()
//
// 	// Test the real implementation (which is not implemented)
// 	_, err := controller.GetTaskById("any-id")
// 	if err == nil || err.Error() != "Not implemented" {
// 		t.Errorf("Expected 'Not implemented' error from controller, got: %v", err)
// 	}
// }

// Testing converters ------------------------------------------------------------------

// TestToTask tests the toTask conversion method
func TestToTask(t *testing.T) {
	reminder := Reminder{
		CreationDate: time.Now(),
		DueDate:      time.Now().Add(24 * time.Hour),
		ExternalID:   "test-id",
		IsCompleted:  true,
		LastModified: time.Now(),
		List:         "TestList",
		Notes:        "Test notes",
		Priority:     1,
		Title:        "Test task",
	}

	task := reminder.toTask()

	if task.Id != reminder.ExternalID {
		t.Errorf("Expected task ID %s, got %s", reminder.ExternalID, task.Id)
	}
	if task.Title != reminder.Title {
		t.Errorf("Expected task title %s, got %s", reminder.Title, task.Title)
	}
	if task.ListId != string(reminder.List) {
		t.Errorf("Expected task listId %s, got %s", string(reminder.List), task.ListId)
	}
	if task.Description != reminder.Notes {
		t.Errorf("Expected task description %s, got %s", reminder.Notes, task.Description)
	}
	if task.Priority != reminder.Priority {
		t.Errorf("Expected task priority %d, got %d", reminder.Priority, task.Priority)
	}
	if task.IsCompleted != reminder.IsCompleted {
		t.Errorf("Expected task isCompleted %v, got %v", reminder.IsCompleted, task.IsCompleted)
	}
	if !task.DueDate.Equal(reminder.DueDate) {
		t.Errorf("Expected task dueDate %v, got %v", reminder.DueDate, task.DueDate)
	}
}

// TestToTasks tests the toTasks conversion method
func TestToTasks(t *testing.T) {
	reminders := Reminders{
		{
			ExternalID:  "id1",
			Title:       "Task 1",
			List:        "List1",
			IsCompleted: false,
		},
		{
			ExternalID:  "id2",
			Title:       "Task 2",
			List:        "List1",
			IsCompleted: true,
		},
	}

	tasks := reminders.toTasks()

	if len(tasks) != len(reminders) {
		t.Errorf("Expected %d tasks, got %d", len(reminders), len(tasks))
	}

	for i, task := range tasks {
		if task.Id != reminders[i].ExternalID {
			t.Errorf("Task %d: Expected ID %s, got %s", i, reminders[i].ExternalID, task.Id)
		}
		if task.Title != reminders[i].Title {
			t.Errorf("Task %d: Expected title %s, got %s", i, reminders[i].Title, task.Title)
		}
		if task.IsCompleted != reminders[i].IsCompleted {
			t.Errorf("Task %d: Expected isCompleted %v, got %v", i, reminders[i].IsCompleted, task.IsCompleted)
		}
	}
}

// TestToReminder tests the toReminder conversion function
func TestToReminder(t *testing.T) {
	task := entities.Task{
		Id:          "test-id",
		Title:       "Test task",
		ListId:      "TestList",
		Description: "Test description",
		DueDate:     time.Now(),
		Priority:    2,
		IsCompleted: true,
	}

	reminder := toReminder(task)

	if reminder.ExternalID != task.Id {
		t.Errorf("Expected reminder externalID %s, got %s", task.Id, reminder.ExternalID)
	}
	if reminder.Title != task.Title {
		t.Errorf("Expected reminder title %s, got %s", task.Title, reminder.Title)
	}
	if string(reminder.List) != task.ListId {
		t.Errorf("Expected reminder list %s, got %s", task.ListId, string(reminder.List))
	}
	if reminder.Notes != task.Description {
		t.Errorf("Expected reminder notes %s, got %s", task.Description, reminder.Notes)
	}
	if reminder.Priority != task.Priority {
		t.Errorf("Expected reminder priority %d, got %d", task.Priority, reminder.Priority)
	}
	if reminder.IsCompleted != task.IsCompleted {
		t.Errorf("Expected reminder isCompleted %v, got %v", task.IsCompleted, reminder.IsCompleted)
	}
	if !reminder.DueDate.Equal(task.DueDate) {
		t.Errorf("Expected reminder dueDate %v, got %v", task.DueDate, reminder.DueDate)
	}
}

// TestToList tests the toList conversion function
func TestToList(t *testing.T) {
	reminderList := ReminderList("TestList")
	list := toList(reminderList)

	if list.Id != string(reminderList) {
		t.Errorf("Expected list ID %s, got %s", string(reminderList), list.Id)
	}
	if list.Title != string(reminderList) {
		t.Errorf("Expected list title %s, got %s", string(reminderList), list.Title)
	}
}

// TestToLists tests the toLists conversion function
func TestToLists(t *testing.T) {
	reminderLists := []ReminderList{"List1", "List2", "List3"}
	lists := toLists(reminderLists)

	if len(lists) != len(reminderLists) {
		t.Errorf("Expected %d lists, got %d", len(reminderLists), len(lists))
	}

	for i, list := range lists {
		if list.Id != string(reminderLists[i]) {
			t.Errorf("List %d: Expected ID %s, got %s", i, string(reminderLists[i]), list.Id)
		}
		if list.Title != string(reminderLists[i]) {
			t.Errorf("List %d: Expected title %s, got %s", i, string(reminderLists[i]), list.Title)
		}
	}
}

// TestToReminderList tests the toReminderList conversion function
func TestToReminderList(t *testing.T) {
	list := entities.List{
		Id:    "TestList",
		Title: "Test List Title",
	}

	reminderList := toReminderList(list)

	if string(reminderList) != list.Id {
		t.Errorf("Expected reminder list %s, got %s", list.Id, string(reminderList))
	}
}

// Testing functions -------------------------------------------------------------

// TestFindProjectRoot tests the findProjectRoot function
func TestFindProjectRoot(t *testing.T) {
	// This is difficult to test reliably in isolation
	// We'll just check that it doesn't return an error
	root, err := findProjectRoot()

	if err != nil {
		t.Errorf("findProjectRoot returned an error: %v", err)
	}

	if root == "" {
		t.Error("findProjectRoot returned an empty path")
	}
}

// TestGetExecutablePath tests the getExecutablePath function
func TestGetExecutablePath(t *testing.T) {
	// Similar to findProjectRoot, this is hard to test precisely
	// We'll just check that it doesn't return an error
	path, err := getExecutablePath()

	if err != nil {
		t.Errorf("getExecutablePath returned an error: %v", err)
	}

	if path == "" {
		t.Error("getExecutablePath returned an empty path")
	}
}

// Helper for checking if a slice contains a value
func slicesContains(slice []string, value string) bool {
	for _, v := range slice {
		if v == value {
			return true
		}
	}
	return false
}

func TestParseJson(t *testing.T) {
	input := []byte(`["a","b"]`)
	got, err := parseJson[[]string](input)
	if err != nil {
		t.Errorf("parseJson() unexpected error: %v", err)
	}
	want := []string{"a", "b"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("parseJson() = %v, want %v", got, want)
	}
	// error case
	if _, err := parseJson[[]int]([]byte(`invalid`)); err == nil {
		t.Errorf("parseJson() expected error on invalid input, got nil")
	}
}

//
// import (
// 	"encoding/json"
// 	"errors"
// 	"lazytask/entities"
// 	"os"
// 	"path/filepath"
// 	"slices"
// 	"strings"
// 	"testing"
// 	"time"
// )
//
//
// func (r Reminder) ToTask() entities.Task {}
// func (reminders Reminders) ToTasks() []entities.Task {}
// func ToReminder(t entities.Task) Reminder {}
// func ToList(r ReminderList) entities.List {}
// func ToLists(rl []ReminderList) []entities.List {}
// func ToReminderList(l entities.List) ReminderList {}
// func findProjectRoot() (string, error) {}
// func getExecutablePath() (string, error) {}
// func parseJson[T any](output []byte) (T, error) {}
// func execCommandWithoutOutput(commandArgs []string) error {}
// func execCommand[T any](commandArgs []string) (T, error) {}
// func getListAndIndexForCompletion(taskId string) (ReminderList, int, error) {}
// func NewReminderTaskController() *ReminderTaskController {}
// func (r ReminderTaskController) GetLists() ([]entities.List, error) {}
// func (r ReminderTaskController) GetListById(listId string) (entities.List, error) {}
// func (r ReminderTaskController) GetTaskById(taskId string) (entities.Task, error) {}
// func (r ReminderTaskController) GetTasksByList(listId string) ([]entities.Task, error) {}
// func (r ReminderTaskController) AddTask(t entities.Task) error {}
// func (r ReminderTaskController) CompleteTask(taskId string) error {}
// func (r ReminderTaskController) UncompleteTask(taskId string) error {}
// func (r ReminderTaskController) UpdateTask(task entities.Task) error {}
// func (r ReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {}
//
//
// // Note on controller method testing:
// // For a real implementation of tests with the current code structure, we would need to:
// // 1. Use a mocking library that can patch functions (like github.com/agiledragon/gomonkey)
// // 2. Patch the `execCommand` and `execCommandWithoutOutput` functions
// // 3. Set up specific expectations for different calls
// //
// // A better approach would be to refactor the code to use dependency injection for the command execution.
// // This would make it possible to inject mock implementations for testing.
//
// // ----------------------------------------------------------------------
//
// // Mock controller implementation for testing
// type MockReminderTaskController struct {
// 	lists []entities.List
// 	tasks map[string][]entities.Task
// }
//
// func NewMockReminderTaskController() *MockReminderTaskController {
// 	return &MockReminderTaskController{
// 		lists: []entities.List{
// 			{Id: "List1", Title: "List 1"},
// 			{Id: "List2", Title: "List 2"},
// 		},
// 		tasks: map[string][]entities.Task{
// 			"List1": {
// 				{Id: "task1", Title: "Task 1", ListId: "List1"},
// 				{Id: "task2", Title: "Task 2", ListId: "List1"},
// 			},
// 			"List2": {
// 				{Id: "task3", Title: "Task 3", ListId: "List2"},
// 			},
// 		},
// 	}
// }
//
// func (m *MockReminderTaskController) GetLists() []entities.List {
// 	return m.lists
// }
//
// func (m *MockReminderTaskController) GetListById(listId string) (entities.List, error) {
// 	for _, list := range m.lists {
// 		if list.Id == listId {
// 			return list, nil
// 		}
// 	}
// 	return entities.List{}, errors.New("List not found")
// }
//
// func (m *MockReminderTaskController) GetTasksByList(listId string) []entities.Task {
// 	return m.tasks[listId]
// }
//
// func (m *MockReminderTaskController) GetTaskById(taskId string) (entities.Task, error) {
// 	for _, tasks := range m.tasks {
// 		for _, task := range tasks {
// 			if task.Id == taskId {
// 				return task, nil
// 			}
// 		}
// 	}
// 	return entities.Task{}, errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) AddTask(task entities.Task) error {
// 	if _, ok := m.tasks[task.ListId]; !ok {
// 		m.tasks[task.ListId] = []entities.Task{}
// 	}
// 	m.tasks[task.ListId] = append(m.tasks[task.ListId], task)
// 	return nil
// }
//
// func (m *MockReminderTaskController) CompleteTask(taskId string) error {
// 	for listId, tasks := range m.tasks {
// 		for i, task := range tasks {
// 			if task.Id == taskId {
// 				m.tasks[listId][i].IsCompleted = true
// 				return nil
// 			}
// 		}
// 	}
// 	return errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) UncompleteTask(taskId string) error {
// 	for listId, tasks := range m.tasks {
// 		for i, task := range tasks {
// 			if task.Id == taskId {
// 				m.tasks[listId][i].IsCompleted = false
// 				return nil
// 			}
// 		}
// 	}
// 	return errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) UpdateTask(task entities.Task) error {
// 	for listId, tasks := range m.tasks {
// 		for i, t := range tasks {
// 			if t.Id == task.Id {
// 				m.tasks[listId][i] = task
// 				return nil
// 			}
// 		}
// 	}
// 	return errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {
// 	var taskToMove entities.Task
// 	var sourceListId string
// 	var taskIndex int
//
// 	// Find the task
// 	found := false
// 	for listId, tasks := range m.tasks {
// 		for i, task := range tasks {
// 			if task.Id == taskId {
// 				taskToMove = task
// 				sourceListId = listId
// 				taskIndex = i
// 				found = true
// 				break
// 			}
// 		}
// 		if found {
// 			break
// 		}
// 	}
//
// 	if !found {
// 		return errors.New("Task not found")
// 	}
//
// 	// Check if target list exists
// 	if _, ok := m.tasks[targetListId]; !ok {
// 		return errors.New("Target list not found")
// 	}
//
// 	// Remove task from source list
// 	m.tasks[sourceListId] = slices.Delete(m.tasks[sourceListId], taskIndex, taskIndex+1)
//
// 	// Update task with new list ID
// 	taskToMove.ListId = targetListId
//
// 	// Add task to target list
// 	m.tasks[targetListId] = append(m.tasks[targetListId], taskToMove)
//
// 	return nil
// }
//
//
//
//
// import (
// 	"encoding/json"
// 	"errors"
// 	"lazytask/entities"
// 	"os"
// 	"path/filepath"
// 	"slices"
// 	"strings"
// 	"testing"
// 	"time"
// )
//
//
// func (r Reminder) ToTask() entities.Task {}
// func (reminders Reminders) ToTasks() []entities.Task {}
// func ToReminder(t entities.Task) Reminder {}
// func ToList(r ReminderList) entities.List {}
// func ToLists(rl []ReminderList) []entities.List {}
// func ToReminderList(l entities.List) ReminderList {}
// func findProjectRoot() (string, error) {}
// func getExecutablePath() (string, error) {}
// func parseJson[T any](output []byte) (T, error) {}
// func execCommandWithoutOutput(commandArgs []string) error {}
// func execCommand[T any](commandArgs []string) (T, error) {}
// func getListAndIndexForCompletion(taskId string) (ReminderList, int, error) {}
// func NewReminderTaskController() *ReminderTaskController {}
// func (r ReminderTaskController) GetLists() ([]entities.List, error) {}
// func (r ReminderTaskController) GetListById(listId string) (entities.List, error) {}
// func (r ReminderTaskController) GetTaskById(taskId string) (entities.Task, error) {}
// func (r ReminderTaskController) GetTasksByList(listId string) ([]entities.Task, error) {}
// func (r ReminderTaskController) AddTask(t entities.Task) error {}
// func (r ReminderTaskController) CompleteTask(taskId string) error {}
// func (r ReminderTaskController) UncompleteTask(taskId string) error {}
// func (r ReminderTaskController) UpdateTask(task entities.Task) error {}
// func (r ReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {}
//
//
// // Note on controller method testing:
// // For a real implementation of tests with the current code structure, we would need to:
// // 1. Use a mocking library that can patch functions (like github.com/agiledragon/gomonkey)
// // 2. Patch the `execCommand` and `execCommandWithoutOutput` functions
// // 3. Set up specific expectations for different calls
// //
// // A better approach would be to refactor the code to use dependency injection for the command execution.
// // This would make it possible to inject mock implementations for testing.
//
// // ----------------------------------------------------------------------
//
// // Mock controller implementation for testing
// type MockReminderTaskController struct {
// 	lists []entities.List
// 	tasks map[string][]entities.Task
// }
//
// func NewMockReminderTaskController() *MockReminderTaskController {
// 	return &MockReminderTaskController{
// 		lists: []entities.List{
// 			{Id: "List1", Title: "List 1"},
// 			{Id: "List2", Title: "List 2"},
// 		},
// 		tasks: map[string][]entities.Task{
// 			"List1": {
// 				{Id: "task1", Title: "Task 1", ListId: "List1"},
// 				{Id: "task2", Title: "Task 2", ListId: "List1"},
// 			},
// 			"List2": {
// 				{Id: "task3", Title: "Task 3", ListId: "List2"},
// 			},
// 		},
// 	}
// }
//
// func (m *MockReminderTaskController) GetLists() []entities.List {
// 	return m.lists
// }
//
// func (m *MockReminderTaskController) GetListById(listId string) (entities.List, error) {
// 	for _, list := range m.lists {
// 		if list.Id == listId {
// 			return list, nil
// 		}
// 	}
// 	return entities.List{}, errors.New("List not found")
// }
//
// func (m *MockReminderTaskController) GetTasksByList(listId string) []entities.Task {
// 	return m.tasks[listId]
// }
//
// func (m *MockReminderTaskController) GetTaskById(taskId string) (entities.Task, error) {
// 	for _, tasks := range m.tasks {
// 		for _, task := range tasks {
// 			if task.Id == taskId {
// 				return task, nil
// 			}
// 		}
// 	}
// 	return entities.Task{}, errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) AddTask(task entities.Task) error {
// 	if _, ok := m.tasks[task.ListId]; !ok {
// 		m.tasks[task.ListId] = []entities.Task{}
// 	}
// 	m.tasks[task.ListId] = append(m.tasks[task.ListId], task)
// 	return nil
// }
//
// func (m *MockReminderTaskController) CompleteTask(taskId string) error {
// 	for listId, tasks := range m.tasks {
// 		for i, task := range tasks {
// 			if task.Id == taskId {
// 				m.tasks[listId][i].IsCompleted = true
// 				return nil
// 			}
// 		}
// 	}
// 	return errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) UncompleteTask(taskId string) error {
// 	for listId, tasks := range m.tasks {
// 		for i, task := range tasks {
// 			if task.Id == taskId {
// 				m.tasks[listId][i].IsCompleted = false
// 				return nil
// 			}
// 		}
// 	}
// 	return errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) UpdateTask(task entities.Task) error {
// 	for listId, tasks := range m.tasks {
// 		for i, t := range tasks {
// 			if t.Id == task.Id {
// 				m.tasks[listId][i] = task
// 				return nil
// 			}
// 		}
// 	}
// 	return errors.New("Task not found")
// }
//
// func (m *MockReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {
// 	var taskToMove entities.Task
// 	var sourceListId string
// 	var taskIndex int
//
// 	// Find the task
// 	found := false
// 	for listId, tasks := range m.tasks {
// 		for i, task := range tasks {
// 			if task.Id == taskId {
// 				taskToMove = task
// 				sourceListId = listId
// 				taskIndex = i
// 				found = true
// 				break
// 			}
// 		}
// 		if found {
// 			break
// 		}
// 	}
//
// 	if !found {
// 		return errors.New("Task not found")
// 	}
//
// 	// Check if target list exists
// 	if _, ok := m.tasks[targetListId]; !ok {
// 		return errors.New("Target list not found")
// 	}
//
// 	// Remove task from source list
// 	m.tasks[sourceListId] = slices.Delete(m.tasks[sourceListId], taskIndex, taskIndex+1)
//
// 	// Update task with new list ID
// 	taskToMove.ListId = targetListId
//
// 	// Add task to target list
// 	m.tasks[targetListId] = append(m.tasks[targetListId], taskToMove)
//
// 	return nil
// }
//
//
