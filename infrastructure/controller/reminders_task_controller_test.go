package infrastructure

import (
	"lazytask/entities"
	"testing"
	"time"
)

// Tests start here
// TestNewReminderTaskController tests the creation of a new controller
func TestNewReminderTaskController(t *testing.T) {
	controller := NewReminderTaskController()

	if controller == nil {
		t.Error("NewReminderTaskController returned nil")
	}
}

// TestGetLists tests retrieving all lists
func TestGetLists(t *testing.T) {
	controller := NewMockReminderTaskController()
	lists, err := controller.GetLists()

	if err != nil {
		t.Errorf("GetLists returned an error: %v", err)
	}

	if len(lists) != 2 {
		t.Errorf("Expected 2 lists, got %d", len(lists))
	}

	// Check command was called correctly
	if len(controller.MockExecutor.CommandCalls) != 1 {
		t.Error("Expected one command call")
	} else if controller.MockExecutor.CommandCalls[0][0] != "show-lists" {
		t.Errorf("Expected 'show-lists' command, got %s", controller.MockExecutor.CommandCalls[0][0])
	}

	// Test error case
	controller.MockExecutor.ShouldFail = true
	_, err = controller.GetLists()
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestGetListById tests retrieving a list by ID
func TestGetListById(t *testing.T) {
	controller := NewMockReminderTaskController()

	// Test existing list
	list, err := controller.GetListById("List1")
	if err != nil {
		t.Errorf("GetListById returned error for existing list: %v", err)
	}
	if list.Id != "List1" || list.Title != "List1" {
		t.Errorf("GetListById returned incorrect list. Expected: {List1, List1}, Got: {%s, %s}",
			list.Id, list.Title)
	}

	// Test non-existent list
	_, err = controller.GetListById("NonExistentList")
	if err == nil {
		t.Error("GetListById did not return error for non-existent list")
	}

	// Test error case from GetLists
	controller.MockExecutor.ShouldFail = true
	_, err = controller.GetListById("List1")
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestGetTasksByList tests retrieving tasks by list ID
func TestGetTasksByList(t *testing.T) {
	controller := NewMockReminderTaskController()

	// Test list with multiple tasks
	listTasks, err := controller.GetTasksByList("List1")
	if err != nil {
		t.Errorf("GetTasksByList returned error: %v", err)
	}
	if len(listTasks) != 2 {
		t.Errorf("Expected 2 tasks for List1, got %d", len(listTasks))
	}

	// Check command was called correctly
	if len(controller.MockExecutor.CommandCalls) != 1 {
		t.Error("Expected one command call")
	} else if controller.MockExecutor.CommandCalls[0][0] != "show" || controller.MockExecutor.CommandCalls[0][1] != "List1" {
		t.Errorf("Expected 'show List1' command, got %v", controller.MockExecutor.CommandCalls[0])
	}

	// Test list with one task
	controller.MockExecutor.CommandCalls = [][]string{} // Reset calls
	listTasks, err = controller.GetTasksByList("List2")
	if err != nil {
		t.Errorf("GetTasksByList returned error: %v", err)
	}
	if len(listTasks) != 1 {
		t.Errorf("Expected 1 task for List2, got %d", len(listTasks))
	}

	// Test error case
	controller.MockExecutor.ShouldFail = true
	_, err = controller.GetTasksByList("List1")
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestAddTask tests adding a task
func TestAddTask(t *testing.T) {
	controller := NewMockReminderTaskController()

	// Test adding task to existing list
	task := entities.Task{
		Id:          "task4",
		Title:       "Task 4",
		ListId:      "List1",
		Description: "Task 4 description",
		DueDate:     time.Now().Add(24 * time.Hour),
		Priority:    1,
	}

	initialRemindersCount := len(controller.MockExecutor.MockReminders)

	err := controller.AddTask(task)
	if err != nil {
		t.Errorf("AddTask returned error: %v", err)
	}

	// Verify command was called correctly
	if len(controller.MockExecutor.CommandCalls) != 1 {
		t.Error("Expected one command call")
	} else if controller.MockExecutor.CommandCalls[0][0] != "add" ||
		controller.MockExecutor.CommandCalls[0][1] != "List1" ||
		controller.MockExecutor.CommandCalls[0][2] != "Task 4" {
		t.Errorf("Expected 'add List1 Task 4' command, got %v", controller.MockExecutor.CommandCalls[0])
	}

	// Verify a new reminder was added to the mock
	if len(controller.MockExecutor.MockReminders) != initialRemindersCount+1 {
		t.Errorf("Expected %d reminders, got %d", initialRemindersCount+1, len(controller.MockExecutor.MockReminders))
	}

	// Test error case
	controller.MockExecutor.ShouldFail = true
	err = controller.AddTask(task)
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestCompleteTask tests completing a task
func TestCompleteTask(t *testing.T) {
	controller := NewMockReminderTaskController()

	// Test completing existing task
	err := controller.CompleteTask("task1")
	if err != nil {
		t.Errorf("CompleteTask returned error: %v", err)
	}

	// Verify command was called correctly
	if len(controller.MockExecutor.CommandCalls) != 1 {
		t.Error("Expected one command call")
	} else if controller.MockExecutor.CommandCalls[0][0] != "complete" ||
		controller.MockExecutor.CommandCalls[0][1] != "List1" {
		t.Errorf("Expected 'complete List1 0' command, got %v", controller.MockExecutor.CommandCalls[0])
	}

	// Verify task was marked as completed in the mock data
	found := false
	for _, reminder := range controller.MockExecutor.MockReminders {
		if reminder.ExternalID == "task1" {
			found = true
			if !reminder.IsCompleted {
				t.Error("Task was not marked as completed")
			}
			break
		}
	}

	if !found {
		t.Error("Task to complete not found in mock data")
	}

	// Test completing non-existent task
	err = controller.CompleteTask("nonexistent")
	if err == nil {
		t.Error("Expected error when completing non-existent task")
	}

	// Test error case
	controller.MockExecutor.ShouldFail = true
	err = controller.CompleteTask("task2")
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestUncompleteTask tests uncompleting a task
func TestUncompleteTask(t *testing.T) {
	controller := NewMockReminderTaskController()

	// First, make sure we have a completed task
	for i, reminder := range controller.MockExecutor.MockReminders {
		if reminder.ExternalID == "task3" {
			controller.MockExecutor.MockReminders[i].IsCompleted = true
			break
		}
	}

	// Reset command calls
	controller.MockExecutor.CommandCalls = [][]string{}

	// Test uncompleting existing task
	err := controller.UncompleteTask("task3")
	if err != nil {
		t.Errorf("UncompleteTask returned error: %v", err)
	}

	// Verify command was called correctly
	if len(controller.MockExecutor.CommandCalls) != 1 {
		t.Error("Expected one command call")
	} else if controller.MockExecutor.CommandCalls[0][0] != "uncomplete" ||
		controller.MockExecutor.CommandCalls[0][1] != "List2" {
		t.Errorf("Expected 'uncomplete List2 0' command, got %v", controller.MockExecutor.CommandCalls[0])
	}

	// Verify task was marked as not completed in the mock data
	found := false
	for _, reminder := range controller.MockExecutor.MockReminders {
		if reminder.ExternalID == "task3" {
			found = true
			if reminder.IsCompleted {
				t.Error("Task was not marked as uncompleted")
			}
			break
		}
	}

	if !found {
		t.Error("Task to uncomplete not found in mock data")
	}

	// Test uncompleting non-existent task
	err = controller.UncompleteTask("nonexistent")
	if err == nil {
		t.Error("Expected error when uncompleting non-existent task")
	}

	// Test error case
	controller.MockExecutor.ShouldFail = true
	err = controller.UncompleteTask("task3")
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestUpdateTask tests updating a task
func TestUpdateTask(t *testing.T) {
	controller := NewMockReminderTaskController()

	// Test updating existing task
	updatedTask := entities.Task{
		Id:          "task1",
		Title:       "Updated Task 1",
		ListId:      "List1",
		Description: "Updated description",
		DueDate:     time.Now().Add(48 * time.Hour),
		Priority:    2,
	}

	err := controller.UpdateTask(updatedTask)
	if err != nil {
		t.Errorf("UpdateTask returned error: %v", err)
	}

	// Verify commands were called correctly
	if len(controller.MockExecutor.CommandCalls) < 2 {
		t.Error("Expected at least two command calls (delete and add)")
	} else {
		deleteCommand := false
		addCommand := false

		for _, call := range controller.MockExecutor.CommandCalls {
			if len(call) > 0 {
				if call[0] == "delete" && call[1] == "List1" {
					deleteCommand = true
				} else if call[0] == "add" && call[1] == "List1" && call[2] == "Updated Task 1" {
					addCommand = true
					// Check for presence of flags
					notesFound := false
					priorityFound := false
					dueDateFound := false

					for i := 3; i < len(call); i++ {
						if call[i] == "--notes" {
							notesFound = true
						} else if call[i] == "--priority" {
							priorityFound = true
						} else if call[i] == "--due-date" {
							dueDateFound = true
						}
					}

					if !notesFound {
						t.Error("Notes flag not found in add command")
					}
					if !priorityFound {
						t.Error("Priority flag not found in add command")
					}
					if !dueDateFound {
						t.Error("Due date flag not found in add command")
					}
				}
			}
		}

		if !deleteCommand {
			t.Error("Delete command not found")
		}
		if !addCommand {
			t.Error("Add command not found")
		}
	}

	// Test updating non-existent task
	nonExistentTask := entities.Task{
		Id:     "nonexistent",
		Title:  "Non-existent Task",
		ListId: "List1",
	}

	err = controller.UpdateTask(nonExistentTask)
	if err == nil {
		t.Error("Expected error when updating non-existent task")
	}

	// Test error case on delete
	controller.MockExecutor.ShouldFail = true
	err = controller.UpdateTask(updatedTask)
	if err == nil {
		t.Error("Expected error when executor fails, got nil")
	}
}

// TestMoveTaskToList tests moving a task to another list
// This feature is not implemented in the controller, so we just test it returns "not implemented"
func TestMoveTaskToList(t *testing.T) {
	controller := NewMockReminderTaskController()

	err := controller.MoveTaskToList("task1", "List2")
	if err == nil || err.Error() != "not implemented" {
		t.Errorf("Expected 'not implemented' error, got: %v", err)
	}
}

// TestGetTaskById tests retrieving a task by ID
func TestGetTaskById(t *testing.T) {
	controller := NewMockReminderTaskController()

	// Test the mock implementation
	task, err := controller.GetTaskById("task1")
	if err != nil {
		t.Errorf("GetTaskById returned error: %v", err)
	}

	if task.Id != "task1" || task.Title != "Task 1" {
		t.Errorf("GetTaskById returned incorrect task. Got: %+v", task)
	}

	// Test non-existent task
	_, err = controller.GetTaskById("nonexistent")
	if err == nil {
		t.Error("Expected error when getting non-existent task")
	}

	// Test the real implementation (which is not implemented)
	realController := NewReminderTaskController()
	_, err = realController.GetTaskById("any-id")
	if err == nil || err.Error() != "Not implemented" {
		t.Errorf("Expected 'Not implemented' error from real controller, got: %v", err)
	}
}


// TODO: add tests for functsions and converters
