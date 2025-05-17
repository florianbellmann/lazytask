package infrastructure

import (
	"testing"
	"time"

	"lazytask/entities"
)

// TestNewInMemoryRepo tests the creation of a new in-memory repository
func TestNewInMemoryRepo(t *testing.T) {
	repo := NewInMemoryRepo()

	if repo == nil {
		t.Error("NewInMemoryRepo returned nil")
	}

	if repo.tasks == nil {
		t.Error("tasks map is nil")
	}

	if repo.lists == nil {
		t.Error("lists map is nil")
	}

	if len(repo.tasks) != 0 {
		t.Errorf("Expected empty tasks map, got %d elements", len(repo.tasks))
	}

	if len(repo.lists) != 0 {
		t.Errorf("Expected empty lists map, got %d elements", len(repo.lists))
	}
}

// TestNewInMemoryRepoWithData tests initializing the repo with data
func TestNewInMemoryRepoWithData(t *testing.T) {
	tasks := []entities.Task{
		{Id: "task1", Title: "Task 1", ListId: "list1"},
		{Id: "task2", Title: "Task 2", ListId: "list2"},
	}

	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
		{Id: "list2", Title: "List 2"},
	}

	repo := NewInMemoryRepoWithData(tasks, lists)

	if repo == nil {
		t.Error("NewInMemoryRepoWithData returned nil")
	}

	if len(repo.tasks) != 2 {
		t.Errorf("Expected 2 tasks, got %d", len(repo.tasks))
	}

	if len(repo.lists) != 2 {
		t.Errorf("Expected 2 lists, got %d", len(repo.lists))
	}

	// Check if tasks are correctly stored
	for _, task := range tasks {
		storedTask, exists := repo.tasks[task.Id]
		if !exists {
			t.Errorf("Task %s not found in repository", task.Id)
		}
		if storedTask.Title != task.Title {
			t.Errorf("Expected task title %s, got %s", task.Title, storedTask.Title)
		}
	}

	// Check if lists are correctly stored
	for _, list := range lists {
		storedList, exists := repo.lists[list.Id]
		if !exists {
			t.Errorf("List %s not found in repository", list.Id)
		}
		if storedList.Title != list.Title {
			t.Errorf("Expected list title %s, got %s", list.Title, storedList.Title)
		}
	}
}

// TestGetLists tests retrieving all lists
func TestGetLists(t *testing.T) {
	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
		{Id: "list2", Title: "List 2"},
	}

	repo := NewInMemoryRepoWithData([]entities.Task{}, lists)

	retrievedLists, err := repo.GetLists()
	if err != nil {
		t.Errorf("GetLists returned error: %v", err)
	}

	if len(retrievedLists) != 2 {
		t.Errorf("Expected 2 lists, got %d", len(retrievedLists))
	}

	// Check if each list exists in the retrieved lists
	for _, expectedList := range lists {
		found := false
		for _, actualList := range retrievedLists {
			if expectedList.Id == actualList.Id && expectedList.Title == actualList.Title {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("List %s not found in retrieved lists", expectedList.Id)
		}
	}
}

// TestGetListById tests retrieving a list by ID
func TestGetListById(t *testing.T) {
	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
		{Id: "list2", Title: "List 2"},
	}

	repo := NewInMemoryRepoWithData([]entities.Task{}, lists)

	// Test existing list
	list, err := repo.GetListById("list1")
	if err != nil {
		t.Errorf("GetListById returned error for existing list: %v", err)
	}
	if list.Id != "list1" || list.Title != "List 1" {
		t.Errorf("GetListById returned incorrect list. Expected: {list1, List 1}, Got: {%s, %s}",
			list.Id, list.Title)
	}

	// Test non-existent list
	_, err = repo.GetListById("nonexistent")
	if err == nil {
		t.Error("GetListById did not return error for non-existent list")
	}
}

// TestGetTaskById tests retrieving a task by ID
func TestGetTaskById(t *testing.T) {
	tasks := []entities.Task{
		{Id: "task1", Title: "Task 1", ListId: "list1"},
		{Id: "task2", Title: "Task 2", ListId: "list2"},
	}

	repo := NewInMemoryRepoWithData(tasks, []entities.List{})

	// Test existing task
	task, err := repo.GetTaskById("task1")
	if err != nil {
		t.Errorf("GetTaskById returned error for existing task: %v", err)
	}
	if task.Id != "task1" || task.Title != "Task 1" {
		t.Errorf("GetTaskById returned incorrect task. Expected: {task1, Task 1}, Got: {%s, %s}",
			task.Id, task.Title)
	}

	// Test non-existent task
	_, err = repo.GetTaskById("nonexistent")
	if err == nil {
		t.Error("GetTaskById did not return error for non-existent task")
	}
}

// TestGetTasksByList tests retrieving tasks by list ID
func TestGetTasksByList(t *testing.T) {
	tasks := []entities.Task{
		{Id: "task1", Title: "Task 1", ListId: "list1"},
		{Id: "task2", Title: "Task 2", ListId: "list1"},
		{Id: "task3", Title: "Task 3", ListId: "list2"},
	}

	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
		{Id: "list2", Title: "List 2"},
	}

	repo := NewInMemoryRepoWithData(tasks, lists)

	// Test list with multiple tasks
	list1Tasks, err := repo.GetTasksByList("list1")
	if err != nil {
		t.Errorf("GetTasksByList returned error: %v", err)
	}
	if len(list1Tasks) != 2 {
		t.Errorf("Expected 2 tasks for list1, got %d", len(list1Tasks))
	}

	// Test list with one task
	list2Tasks, err := repo.GetTasksByList("list2")
	if err != nil {
		t.Errorf("GetTasksByList returned error: %v", err)
	}
	if len(list2Tasks) != 1 {
		t.Errorf("Expected 1 task for list2, got %d", len(list2Tasks))
	}

	// Test non-existent list (should return empty array, not error)
	nonExistentListTasks, err := repo.GetTasksByList("nonexistent")
	if err != nil {
		t.Errorf("GetTasksByList returned error for non-existent list: %v", err)
	}
	if len(nonExistentListTasks) != 0 {
		t.Errorf("Expected 0 tasks for non-existent list, got %d", len(nonExistentListTasks))
	}
}

// TestAddTask tests adding a task
func TestAddTask(t *testing.T) {
	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
	}

	repo := NewInMemoryRepoWithData([]entities.Task{}, lists)

	// Test adding task to existing list
	task := entities.Task{
		Id:          "task1",
		Title:       "Task 1",
		ListId:      "list1",
		Description: "Description 1",
		DueDate:     time.Now(),
		Priority:    1,
	}

	err := repo.AddTask(task)
	if err != nil {
		t.Errorf("AddTask returned error for valid task: %v", err)
	}

	// Verify task was added
	addedTask, err := repo.GetTaskById("task1")
	if err != nil {
		t.Errorf("Could not retrieve added task: %v", err)
	}
	if addedTask.Id != "task1" || addedTask.Title != "Task 1" {
		t.Errorf("Retrieved task doesn't match added task")
	}

	// Test adding task to non-existent list (should return error)
	invalidTask := entities.Task{
		Id:     "task2",
		Title:  "Task 2",
		ListId: "nonexistent",
	}

	err = repo.AddTask(invalidTask)
	if err == nil {
		t.Error("AddTask did not return error for non-existent list")
	}
}

// TestCompleteTask tests completing a task
func TestCompleteTask(t *testing.T) {
	tasks := []entities.Task{
		{Id: "task1", Title: "Task 1", ListId: "list1"},
	}

	repo := NewInMemoryRepoWithData(tasks, []entities.List{})

	// Test completing existing task
	err := repo.CompleteTask("task1")
	if err != nil {
		t.Errorf("CompleteTask returned error for existing task: %v", err)
	}

	// Verify task was deleted (completion in this repo means deletion)
	_, err = repo.GetTaskById("task1")
	if err == nil {
		t.Error("Task was not deleted after completion")
	}

	// Test completing non-existent task
	err = repo.CompleteTask("nonexistent")
	if err == nil {
		t.Error("CompleteTask did not return error for non-existent task")
	}
}

// TestUncompleteTask tests uncompleting a task (which is not implemented)
func TestUncompleteTask(t *testing.T) {
	repo := NewInMemoryRepo()

	err := repo.UncompleteTask("any-task")
	if err == nil {
		t.Error("UncompleteTask did not return error as expected")
	}
}

// TestUpdateTask tests updating a task
func TestUpdateTask(t *testing.T) {
	tasks := []entities.Task{
		{Id: "task1", Title: "Task 1", ListId: "list1", Priority: 1},
	}

	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
		{Id: "list2", Title: "List 2"},
	}

	repo := NewInMemoryRepoWithData(tasks, lists)

	// Test updating existing task
	updatedTask := entities.Task{
		Id:          "task1",
		Title:       "Updated Task 1",
		ListId:      "list1",
		Description: "Updated description",
		Priority:    2,
	}

	result, err := repo.UpdateTask(updatedTask)
	if err != nil {
		t.Errorf("UpdateTask returned error for existing task: %v", err)
	}

	// Verify task was updated
	if result.Title != "Updated Task 1" || result.Description != "Updated description" || result.Priority != 2 {
		t.Error("Task was not updated correctly")
	}

	// Verify using GetTaskById
	retrievedTask, err := repo.GetTaskById("task1")
	if err != nil {
		t.Errorf("Could not retrieve updated task: %v", err)
	}
	if retrievedTask.Title != "Updated Task 1" || retrievedTask.Description != "Updated description" || retrievedTask.Priority != 2 {
		t.Error("Retrieved task doesn't reflect updates")
	}

	// Test updating non-existent task
	nonExistentTask := entities.Task{
		Id:     "nonexistent",
		Title:  "Non-existent Task",
		ListId: "list1",
	}

	_, err = repo.UpdateTask(nonExistentTask)
	if err == nil {
		t.Error("UpdateTask did not return error for non-existent task")
	}

	// Test updating task with non-existent list
	invalidListTask := entities.Task{
		Id:     "task1",
		Title:  "Task with invalid list",
		ListId: "nonexistent",
	}

	_, err = repo.UpdateTask(invalidListTask)
	if err == nil {
		t.Error("UpdateTask did not return error for non-existent list")
	}
}

// TestMoveTaskToList tests moving a task to another list
func TestMoveTaskToList(t *testing.T) {
	tasks := []entities.Task{
		{Id: "task1", Title: "Task 1", ListId: "list1"},
	}

	lists := []entities.List{
		{Id: "list1", Title: "List 1"},
		{Id: "list2", Title: "List 2"},
	}

	repo := NewInMemoryRepoWithData(tasks, lists)

	// Test moving task to a different list
	err := repo.MoveTaskToList("task1", "list2")
	if err != nil {
		t.Errorf("MoveTaskToList returned error: %v", err)
	}

	// Verify task was moved
	movedTask, err := repo.GetTaskById("task1")
	if err != nil {
		t.Errorf("Could not retrieve moved task: %v", err)
	}
	if movedTask.ListId != "list2" {
		t.Errorf("Task was not moved to the correct list. Expected list2, got %s", movedTask.ListId)
	}

	// Test moving non-existent task
	err = repo.MoveTaskToList("nonexistent", "list2")
	if err == nil {
		t.Error("MoveTaskToList did not return error for non-existent task")
	}

	// Test moving to non-existent list
	err = repo.MoveTaskToList("task1", "nonexistent")
	if err == nil {
		t.Error("MoveTaskToList did not return error for non-existent target list")
	}
}

