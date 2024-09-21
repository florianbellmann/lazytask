package application

import (
	"lazytask/domain"
)

type TaskService struct {
	taskCtrl domain.TaskController
}

func NewTaskService(taskCtrl domain.TaskController) *TaskService {
	return &TaskService{taskCtrl: taskCtrl}
}

// Add a new task
func (s *TaskService) AddTask(task domain.Task) error {
	return s.taskCtrl.AddTask(task)
}

// Complete a task by its ID
func (s *TaskService) CompleteTask(taskId string) error {
	return s.taskCtrl.CompleteTask(taskId)
}

// Uncomplete a task by its ID
func (s *TaskService) UncompleteTask(taskId string) error {
	return s.taskCtrl.UncompleteTask(taskId)
}

// Get tasks by a specific list ID
func (s *TaskService) GetTasksByList(listId string) []domain.Task {
	return s.taskCtrl.GetTasksByList(listId)
}

// Get all task lists
func (s *TaskService) GetLists() []domain.List {
	return s.taskCtrl.GetLists()
}
