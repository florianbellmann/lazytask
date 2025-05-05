package infrastructure_test

import (
	"encoding/json"
	"errors"
	"lazytask/domain"
	"lazytask/infrastructure"
	"log"
	"strings"
	"testing"
	"time"
)

// Test parsing of ReminderLists to domain.Lists
func TestListParsing(t *testing.T) {
	mockResponse := `[
	"FirstList",
	"Second list",
	"Third list"
	]` // Even with trailing comma, it should parse correctly

	var reminderLists []ReminderList
	err := json.Unmarshal([]byte(mockResponse), &reminderLists)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %s", err)
	}

	// log.Printf("Reminder lists: %v", reminderLists)

	lists := parseLists(reminderLists)
	if lists[0].Id != "FirstList" ||
		lists[1].Id != "Second list" ||
		lists[2].Id != "Third list" ||
		len(lists) != 3 {
		t.Errorf("Failed to parse lists")
	}

}

func TestParseEmptyList(t *testing.T) {
	mockResponse := "[]"

	var reminderLists []ReminderList
	json.Unmarshal([]byte(mockResponse), &reminderLists)

	lists := parseLists(reminderLists)
	if len(lists) != 0 {
		t.Errorf("Failed to parse empty list")
	}
}

func TestGetListIndex(t *testing.T) {
	taskId := "810AE4D8-82FC-45BF-A0D2-C25E6205B178"
	listName, listIndex, err := getListAndIndexForCompletion(taskId)

	if err != nil {
		log.Printf("Error: %s", err)
		log.Printf("Error contains: %s", strings.Contains(err.Error(), "lazytask/adapters/reminders-cli/reminders"))
		if strings.Contains(err.Error(), "lazytask/adapters/reminders-cli/reminders") && !strings.Contains(err.Error(), "florian") { // means it failed on the workflow
			log.Printf("Failed to get index and list for: %s", taskId)
		} else {
			log.Fatalf("Failed to get index and list for: %s", taskId)
		}
	}

	if listName != "develop" || listIndex != 1 {
		t.Errorf("Failed to get the correct listName or listIndex")
	}
}

func TestReminderToTask(t *testing.T) {
	dueDate := time.Now()
	reminder := Reminder{
		DueDate:     dueDate,
		ExternalID:  "test-id",
		IsCompleted: true,
		List:        "TestList",
		Notes:       "Test description",
		Priority:    1,
		Title:       "Test task",
	}

	task := reminder.ToTask()

	if task.DueDate != dueDate {
		t.Errorf("Expected DueDate to be %v, got %v", dueDate, task.DueDate)
	}
	if task.Id != "test-id" {
		t.Errorf("Expected Id to be test-id, got %s", task.Id)
	}
	if !task.IsCompleted {
		t.Errorf("Expected IsCompleted to be true")
	}
	if task.ListId != "TestList" {
		t.Errorf("Expected ListId to be TestList, got %s", task.ListId)
	}
	if task.Description != "Test description" {
		t.Errorf("Expected Description to be 'Test description', got %s", task.Description)
	}
	if task.Priority != 1 {
		t.Errorf("Expected Priority to be 1, got %d", task.Priority)
	}
	if task.Title != "Test task" {
		t.Errorf("Expected Title to be 'Test task', got %s", task.Title)
	}
}

func TestTaskToReminder(t *testing.T) {
	dueDate := time.Now()
	task := domain.Task{
		DueDate:     dueDate,
		Id:          "test-id",
		IsCompleted: true,
		ListId:      "TestList",
		Description: "Test description",
		Priority:    1,
		Title:       "Test task",
	}

	reminder := ReminderFromTask(task)

	if reminder.DueDate != dueDate {
		t.Errorf("Expected DueDate to be %v, got %v", dueDate, reminder.DueDate)
	}
	if reminder.ExternalID != "test-id" {
		t.Errorf("Expected ExternalID to be test-id, got %s", reminder.ExternalID)
	}
	if !reminder.IsCompleted {
		t.Errorf("Expected IsCompleted to be true")
	}
	if reminder.List != "TestList" {
		t.Errorf("Expected List to be TestList, got %s", reminder.List)
	}
	if reminder.Notes != "Test description" {
		t.Errorf("Expected Notes to be 'Test description', got %s", reminder.Notes)
	}
	if reminder.Priority != 1 {
		t.Errorf("Expected Priority to be 1, got %d", reminder.Priority)
	}
	if reminder.Title != "Test task" {
		t.Errorf("Expected Title to be 'Test task', got %s", reminder.Title)
	}
}

func TestReminderListToList(t *testing.T) {
	reminderList := ReminderList("TestList")
	list := ReminderListToList(reminderList)

	if list.Id != "TestList" {
		t.Errorf("Expected Id to be TestList, got %s", list.Id)
	}
	if list.Title != "TestList" {
		t.Errorf("Expected Title to be TestList, got %s", list.Title)
	}
}

func TestListToReminderList(t *testing.T) {
	list := domain.List{
		Id:    "TestList",
		Title: "Test List Title",
	}
	reminderList := ListToReminderList(list)

	if reminderList != "TestList" {
		t.Errorf("Expected ReminderList to be TestList, got %s", reminderList)
	}
}

func TestParseTasks(t *testing.T) {
	dueDate := time.Now()
	reminders := []Reminder{
		{
			DueDate:     dueDate,
			ExternalID:  "test-id-1",
			IsCompleted: true,
			List:        "TestList",
			Notes:       "Test description 1",
			Priority:    1,
			Title:       "Test task 1",
		},
		{
			DueDate:     dueDate.Add(24 * time.Hour),
			ExternalID:  "test-id-2",
			IsCompleted: false,
			List:        "TestList",
			Notes:       "Test description 2",
			Priority:    2,
			Title:       "Test task 2",
		},
	}

	tasks := parseTasks(reminders)

	if len(tasks) != 2 {
		t.Errorf("Expected 2 tasks, got %d", len(tasks))
	}

	if tasks[0].Id != "test-id-1" || tasks[1].Id != "test-id-2" {
		t.Errorf("Task IDs not correctly parsed")
	}

	if tasks[0].Title != "Test task 1" || tasks[1].Title != "Test task 2" {
		t.Errorf("Task titles not correctly parsed")
	}
}

// Mock controller implementation for testing
type MockReminderTaskController struct {
	lists []domain.List
	tasks map[string][]domain.Task
}

func NewMockReminderTaskController() *MockReminderTaskController {
	return &MockReminderTaskController{
		lists: []domain.List{
			{Id: "List1", Title: "List 1"},
			{Id: "List2", Title: "List 2"},
		},
		tasks: map[string][]domain.Task{
			"List1": {
				{Id: "task1", Title: "Task 1", ListId: "List1"},
				{Id: "task2", Title: "Task 2", ListId: "List1"},
			},
			"List2": {
				{Id: "task3", Title: "Task 3", ListId: "List2"},
			},
		},
	}
}

func (m *MockReminderTaskController) GetLists() []domain.List {
	return m.lists
}

func (m *MockReminderTaskController) GetListById(listId string) (domain.List, error) {
	for _, list := range m.lists {
		if list.Id == listId {
			return list, nil
		}
	}
	return domain.List{}, errors.New("List not found")
}

func (m *MockReminderTaskController) GetTasksByList(listId string) []domain.Task {
	return m.tasks[listId]
}

func (m *MockReminderTaskController) GetTaskById(taskId string) (domain.Task, error) {
	for _, tasks := range m.tasks {
		for _, task := range tasks {
			if task.Id == taskId {
				return task, nil
			}
		}
	}
	return domain.Task{}, errors.New("Task not found")
}

func (m *MockReminderTaskController) AddTask(task domain.Task) error {
	if _, ok := m.tasks[task.ListId]; !ok {
		m.tasks[task.ListId] = []domain.Task{}
	}
	m.tasks[task.ListId] = append(m.tasks[task.ListId], task)
	return nil
}

func (m *MockReminderTaskController) CompleteTask(taskId string) error {
	for listId, tasks := range m.tasks {
		for i, task := range tasks {
			if task.Id == taskId {
				m.tasks[listId][i].IsCompleted = true
				return nil
			}
		}
	}
	return errors.New("Task not found")
}

func (m *MockReminderTaskController) UncompleteTask(taskId string) error {
	for listId, tasks := range m.tasks {
		for i, task := range tasks {
			if task.Id == taskId {
				m.tasks[listId][i].IsCompleted = false
				return nil
			}
		}
	}
	return errors.New("Task not found")
}

func (m *MockReminderTaskController) UpdateTask(task domain.Task) error {
	for listId, tasks := range m.tasks {
		for i, t := range tasks {
			if t.Id == task.Id {
				m.tasks[listId][i] = task
				return nil
			}
		}
	}
	return errors.New("Task not found")
}

func (m *MockReminderTaskController) MoveTaskToList(taskId string, targetListId string) error {
	var taskToMove domain.Task
	var sourceListId string
	var taskIndex int

	// Find the task
	found := false
	for listId, tasks := range m.tasks {
		for i, task := range tasks {
			if task.Id == taskId {
				taskToMove = task
				sourceListId = listId
				taskIndex = i
				found = true
				break
			}
		}
		if found {
			break
		}
	}

	if !found {
		return errors.New("Task not found")
	}

	// Check if target list exists
	if _, ok := m.tasks[targetListId]; !ok {
		return errors.New("Target list not found")
	}

	// Remove task from source list
	m.tasks[sourceListId] = append(m.tasks[sourceListId][:taskIndex], m.tasks[sourceListId][taskIndex+1:]...)

	// Update task with new list ID
	taskToMove.ListId = targetListId

	// Add task to target list
	m.tasks[targetListId] = append(m.tasks[targetListId], taskToMove)

	return nil
}

func TestMockControllerGetLists(t *testing.T) {
	controller := NewMockReminderTaskController()
	lists := controller.GetLists()

	if len(lists) != 2 {
		t.Errorf("Expected 2 lists, got %d", len(lists))
	}
	if lists[0].Id != "List1" || lists[1].Id != "List2" {
		t.Errorf("Incorrect list IDs")
	}
}

func TestMockControllerGetListById(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	// Test existing list
	list, err := controller.GetListById("List1")
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if list.Id != "List1" || list.Title != "List 1" {
		t.Errorf("Incorrect list returned")
	}
	
	// Test non-existent list
	_, err = controller.GetListById("NonExistentList")
	if err == nil {
		t.Errorf("Expected error for non-existent list")
	}
}

func TestMockControllerGetTasksByList(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	tasks := controller.GetTasksByList("List1")
	if len(tasks) != 2 {
		t.Errorf("Expected 2 tasks, got %d", len(tasks))
	}
	if tasks[0].Id != "task1" || tasks[1].Id != "task2" {
		t.Errorf("Incorrect task IDs")
	}
	
	// Test empty list
	tasks = controller.GetTasksByList("NonExistentList")
	if len(tasks) != 0 {
		t.Errorf("Expected 0 tasks for non-existent list, got %d", len(tasks))
	}
}

func TestMockControllerAddTask(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	// Add task to existing list
	newTask := domain.Task{
		Id:     "task4",
		Title:  "Task 4",
		ListId: "List1",
	}
	
	err := controller.AddTask(newTask)
	if err != nil {
		t.Errorf("Failed to add task: %v", err)
	}
	
	tasks := controller.GetTasksByList("List1")
	if len(tasks) != 3 {
		t.Errorf("Expected 3 tasks after adding, got %d", len(tasks))
	}
	
	// Add task to new list
	newTask2 := domain.Task{
		Id:     "task5",
		Title:  "Task 5",
		ListId: "List3",
	}
	
	err = controller.AddTask(newTask2)
	if err != nil {
		t.Errorf("Failed to add task to new list: %v", err)
	}
	
	tasks = controller.GetTasksByList("List3")
	if len(tasks) != 1 {
		t.Errorf("Expected 1 task in new list, got %d", len(tasks))
	}
}

func TestMockControllerCompleteTask(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	// Complete task
	err := controller.CompleteTask("task1")
	if err != nil {
		t.Errorf("Failed to complete task: %v", err)
	}
	
	// Check if task is completed
	for _, task := range controller.GetTasksByList("List1") {
		if task.Id == "task1" && !task.IsCompleted {
			t.Errorf("Task1 should be completed")
		}
	}
	
	// Try to complete non-existent task
	err = controller.CompleteTask("nonexistent")
	if err == nil {
		t.Errorf("Expected error when completing non-existent task")
	}
}

func TestMockControllerUncompleteTask(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	// First complete a task
	controller.CompleteTask("task1")
	
	// Now uncomplete it
	err := controller.UncompleteTask("task1")
	if err != nil {
		t.Errorf("Failed to uncomplete task: %v", err)
	}
	
	// Check if task is uncompleted
	for _, task := range controller.GetTasksByList("List1") {
		if task.Id == "task1" && task.IsCompleted {
			t.Errorf("Task1 should be uncompleted")
		}
	}
}

func TestMockControllerUpdateTask(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	// Update task
	updatedTask := domain.Task{
		Id:          "task1",
		Title:       "Updated Task 1",
		Description: "Updated description",
		ListId:      "List1",
		Priority:    2,
	}
	
	err := controller.UpdateTask(updatedTask)
	if err != nil {
		t.Errorf("Failed to update task: %v", err)
	}
	
	// Check if task was updated
	tasks := controller.GetTasksByList("List1")
	found := false
	for _, task := range tasks {
		if task.Id == "task1" {
			found = true
			if task.Title != "Updated Task 1" || 
			   task.Description != "Updated description" ||
			   task.Priority != 2 {
				t.Errorf("Task not updated correctly")
			}
		}
	}
	
	if !found {
		t.Errorf("Updated task not found")
	}
	
	// Try to update non-existent task
	nonExistentTask := domain.Task{
		Id:    "nonexistent",
		Title: "Non-existent Task",
	}
	
	err = controller.UpdateTask(nonExistentTask)
	if err == nil {
		t.Errorf("Expected error when updating non-existent task")
	}
}

func TestMockControllerMoveTaskToList(t *testing.T) {
	controller := NewMockReminderTaskController()
	
	// Initial counts
	list1Tasks := controller.GetTasksByList("List1")
	list2Tasks := controller.GetTasksByList("List2")
	
	initialList1Count := len(list1Tasks)
	initialList2Count := len(list2Tasks)
	
	// Move task from List1 to List2
	err := controller.MoveTaskToList("task1", "List2")
	if err != nil {
		t.Errorf("Failed to move task: %v", err)
	}
	
	// Check counts after move
	list1TasksAfter := controller.GetTasksByList("List1")
	list2TasksAfter := controller.GetTasksByList("List2")
	
	if len(list1TasksAfter) != initialList1Count-1 {
		t.Errorf("Expected List1 to have %d tasks after move, got %d", initialList1Count-1, len(list1TasksAfter))
	}
	
	if len(list2TasksAfter) != initialList2Count+1 {
		t.Errorf("Expected List2 to have %d tasks after move, got %d", initialList2Count+1, len(list2TasksAfter))
	}
	
	// Check if task exists in List2 with correct ListId
	found := false
	for _, task := range list2TasksAfter {
		if task.Id == "task1" {
			found = true
			if task.ListId != "List2" {
				t.Errorf("Task ListId not updated correctly after move")
			}
		}
	}
	
	if !found {
		t.Errorf("Moved task not found in target list")
	}
	
	// Try to move non-existent task
	err = controller.MoveTaskToList("nonexistent", "List2")
	if err == nil {
		t.Errorf("Expected error when moving non-existent task")
	}
	
	// Try to move to non-existent list
	err = controller.MoveTaskToList("task2", "NonExistentList")
	if err == nil {
		t.Errorf("Expected error when moving to non-existent list")
	}
}
