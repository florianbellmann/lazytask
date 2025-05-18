package infrastructure

import (
	"errors"
	"fmt"
	"lazytask/entities"
	"time"
)

// MockExecutor is a mock implementation that replaces the exec.Command execution
// This allows us to test the controller without actually executing CLI commands
type MockExecutor struct {
	// Track calls to commands for verification
	CommandCalls     [][]string
	MockLists        []ReminderList
	MockReminders    Reminders
	MockReminderById Reminder
	ShouldFail       bool
}

// Mock implementation of execCommand
func (m *MockExecutor) execCommand(commandArgs []string) (interface{}, error) {
	// Record the call
	m.CommandCalls = append(m.CommandCalls, commandArgs)

	// Check if we should simulate failure
	if m.ShouldFail {
		return nil, errors.New("mock executor error")
	}

	// Return appropriate mock data based on the command
	if len(commandArgs) > 0 {
		command := commandArgs[0]
		switch command {
		case "show-lists":
			return m.MockLists, nil
		case "show-all":
			return m.MockReminders, nil
		case "show":
			if len(commandArgs) > 1 {
				listName := commandArgs[1]
				// Filter reminders that belong to the requested list
				filteredReminders := Reminders{}
				for _, reminder := range m.MockReminders {
					if string(reminder.List) == listName {
						filteredReminders = append(filteredReminders, reminder)
					}
				}
				return filteredReminders, nil
			}
			return Reminders{}, nil
		case "add":
			// Mock adding a reminder and return it
			newReminder := Reminder{
				ExternalID:   "new-mock-id",
				Title:        commandArgs[2],
				List:         ReminderList(commandArgs[1]),
				CreationDate: time.Now(),
				LastModified: time.Now(),
			}

			// Process additional args
			for i := 3; i < len(commandArgs); i += 2 {
				if i+1 < len(commandArgs) {
					flag := commandArgs[i]
					value := commandArgs[i+1]

					switch flag {
					case "--notes":
						newReminder.Notes = value
					case "--priority":
						switch value {
						case "high":
							newReminder.Priority = 1
						case "medium":
							newReminder.Priority = 2
						case "low":
							newReminder.Priority = 5
						}
					case "--due-date":
						// Simple date parsing - in a real implementation would need more robust handling
						dueDate, _ := time.Parse("2006-01-02", value)
						newReminder.DueDate = dueDate
					}
				}
			}

			// Add to mock reminders
			m.MockReminders = append(m.MockReminders, newReminder)
			return newReminder, nil
		}
	}

	// Default fallback
	return nil, nil
}

// Mock implementation of execCommandWithoutOutput
func (m *MockExecutor) execCommandWithoutOutput(commandArgs []string) error {
	// Record the call
	m.CommandCalls = append(m.CommandCalls, commandArgs)

	// Check if we should simulate failure
	if m.ShouldFail {
		return errors.New("mock executor error")
	}

	// Handle complete/uncomplete/delete commands
	if len(commandArgs) > 0 {
		command := commandArgs[0]
		switch command {
		case "complete":
			// Mark the task as completed
			if len(commandArgs) > 2 {
				listName := commandArgs[1]
				// In a real implementation, would use the index to find the task
				// For mock, we'll just mark tasks in that list as completed
				for i := range m.MockReminders {
					if m.MockReminders[i].List == ReminderList(listName) {
						m.MockReminders[i].IsCompleted = true
						break
					}
				}
			}
		case "uncomplete":
			// Mark the task as not completed
			if len(commandArgs) > 2 {
				listName := commandArgs[1]
				// For mock, we'll just mark tasks in that list as not completed
				for i := range m.MockReminders {
					if m.MockReminders[i].List == ReminderList(listName) {
						m.MockReminders[i].IsCompleted = false
						break
					}
				}
			}
		case "delete":
			// Remove a task
			if len(commandArgs) > 2 {
				listName := commandArgs[1]
				// Simple mock deletion - in real implementation would use the index
				for i := range m.MockReminders {
					if m.MockReminders[i].List == ReminderList(listName) {
						// Remove this reminder from the slice
						m.MockReminders = append(m.MockReminders[:i], m.MockReminders[i+1:]...)
						break
					}
				}
			}
		}
	}

	return nil
}

// MockReminderTaskController is a testable version of ReminderTaskController that uses the MockExecutor
type MockReminderTaskController struct {
	ReminderTaskController
	MockExecutor *MockExecutor
}

// Create a new instance of MockReminderTaskController with pre-populated test data
func NewMockReminderTaskController() *MockReminderTaskController {
	currentTime := time.Now()

	// Create mock data
	mockLists := []ReminderList{"List1", "List2"}
	mockReminders := Reminders{
		{
			CreationDate: currentTime.Add(-48 * time.Hour),
			DueDate:      currentTime.Add(24 * time.Hour),
			ExternalID:   "task1",
			IsCompleted:  false,
			LastModified: currentTime.Add(-24 * time.Hour),
			List:         "List1",
			Notes:        "Task 1 notes",
			Priority:     1,
			Title:        "Task 1",
		},
		{
			CreationDate: currentTime.Add(-24 * time.Hour),
			DueDate:      currentTime.Add(48 * time.Hour),
			ExternalID:   "task2",
			IsCompleted:  false,
			LastModified: currentTime,
			List:         "List1",
			Notes:        "Task 2 notes",
			Priority:     2,
			Title:        "Task 2",
		},
		{
			CreationDate: currentTime.Add(-12 * time.Hour),
			DueDate:      currentTime.Add(72 * time.Hour),
			ExternalID:   "task3",
			IsCompleted:  true,
			LastModified: currentTime,
			List:         "List2",
			Notes:        "Task 3 notes",
			Priority:     5,
			Title:        "Task 3",
		},
	}

	// Create the mock executor
	mockExecutor := &MockExecutor{
		CommandCalls:  [][]string{},
		MockLists:     mockLists,
		MockReminders: mockReminders,
		ShouldFail:    false,
	}

	// Create the controller with the mock executor
	controller := &MockReminderTaskController{
		MockExecutor: mockExecutor,
	}

	return controller
}

// Override controller methods to use the mock executor

func (m *MockReminderTaskController) GetLists() ([]entities.List, error) {
	reminderLists, err := m.MockExecutor.execCommand([]string{"show-lists"})
	if err != nil {
		return []entities.List{}, err
	}

	// Type assertion for our mock
	lists, ok := reminderLists.([]ReminderList)
	if !ok {
		return []entities.List{}, errors.New("failed to cast result to []ReminderList")
	}

	return toLists(lists), nil
}

func (m *MockReminderTaskController) GetListById(listId string) (entities.List, error) {
	lists, err := m.GetLists()
	if err != nil {
		return entities.List{}, err
	}

	for _, list := range lists {
		if list.Id == listId {
			return list, nil
		}
	}

	return entities.List{}, errors.New("list not found through controller")
}

func (m *MockReminderTaskController) GetTasksByList(listId string) ([]entities.Task, error) {
	result, err := m.MockExecutor.execCommand([]string{"show", listId})
	if err != nil {
		return []entities.Task{}, fmt.Errorf("failed to get tasks for list: %w", err)
	}

	// Type assertion for our mock
	reminders, ok := result.(Reminders)
	if !ok {
		return []entities.Task{}, errors.New("failed to cast result to Reminders")
	}

	return reminders.toTasks(), nil
}

func (m *MockReminderTaskController) AddTask(t entities.Task) error {
	reminder := toReminder(t)

	commandString := []string{"add", reminder.List, reminder.Title}

	if reminder.Notes != "" {
		commandString = append(commandString, "--notes", reminder.Notes)
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

	_, err := m.MockExecutor.execCommand(commandString)
	if err != nil {
		return fmt.Errorf("failed to add task: %w", err)
	}

	return nil
}

func (m *MockReminderTaskController) CompleteTask(taskId string) error {
	// Mock implementation of getListAndIndexForCompletion logic
	for i, reminder := range m.MockExecutor.MockReminders {
		if reminder.ExternalID == taskId {
			listName := reminder.List
			err := m.MockExecutor.execCommandWithoutOutput([]string{"complete", string(listName), "0"}) // Using 0 as dummy index
			if err != nil {
				return fmt.Errorf("failed to complete task: %w", err)
			}
			// Update the mock data directly
			m.MockExecutor.MockReminders[i].IsCompleted = true
			return nil
		}
	}

	return errors.New("task not found")
}

func (m *MockReminderTaskController) UncompleteTask(taskId string) error {
	// Similar to CompleteTask but marks as uncompleted
	for i, reminder := range m.MockExecutor.MockReminders {
		if reminder.ExternalID == taskId && reminder.IsCompleted {
			listName := reminder.List
			err := m.MockExecutor.execCommandWithoutOutput([]string{"uncomplete", string(listName), "0"}) // Using 0 as dummy index
			if err != nil {
				return fmt.Errorf("failed to uncomplete task: %w", err)
			}
			// Update the mock data directly
			m.MockExecutor.MockReminders[i].IsCompleted = false
			return nil
		}
	}

	return errors.New("completed task not found")
}

func (m *MockReminderTaskController) UpdateTask(task entities.Task) error {
	// Find the task to update
	found := false
	var listName ReminderList
	for _, reminder := range m.MockExecutor.MockReminders {
		if reminder.ExternalID == task.Id {
			found = true
			listName = reminder.List
			break
		}
	}

	if !found {
		return errors.New("task not found for update")
	}

	// Delete the existing task
	deleteArgs := []string{"delete", string(listName), "0"} // dummy index
	err := m.MockExecutor.execCommandWithoutOutput(deleteArgs)
	if err != nil {
		return fmt.Errorf("failed to delete task for update: %w", err)
	}

	// Create a new task with updated properties
	addArgs := []string{"add", string(listName), task.Title}

	if task.Description != "" {
		addArgs = append(addArgs, "--notes", task.Description)
	}

	if !task.DueDate.IsZero() {
		dateString := task.DueDate.Format("2006-01-02")
		addArgs = append(addArgs, "--due-date", dateString)
	}

	if task.Priority != 0 {
		prioString := "none"
		if task.Priority == 1 {
			prioString = "high"
		} else if task.Priority > 1 {
			prioString = "medium"
		} else if task.Priority > 5 {
			prioString = "low"
		}
		addArgs = append(addArgs, "--priority", prioString)
	}

	_, err = m.MockExecutor.execCommand(addArgs)
	if err != nil {
		return fmt.Errorf("failed to recreate task: %w", err)
	}

	return nil
}

func (m *MockReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {
	return errors.New("not implemented")
}

// GetTaskById implementation for the mock
func (m *MockReminderTaskController) GetTaskById(taskId string) (entities.Task, error) {
	for _, reminder := range m.MockExecutor.MockReminders {
		if reminder.ExternalID == taskId {
			return reminder.toTask(), nil
		}
	}

	return entities.Task{}, errors.New("task not found by ID")
}
