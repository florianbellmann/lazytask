package infrastructure

import (
	"errors"
	"fmt"
	entities "lazytask/entities"
	"log"
)

type InMemoryRepo struct {
	tasks map[string]entities.Task
	lists map[string]entities.List
}

func NewInMemoryRepo() *InMemoryRepo {
	log.Printf("In-memory repository initialized.")
	return &InMemoryRepo{
		tasks: make(map[string]entities.Task),
		lists: make(map[string]entities.List),
	}
}

func NewInMemoryRepoWithData(tasks []entities.Task, lists []entities.List) *InMemoryRepo {
	log.Printf("In-memory repository initialized with data.")
	repo := NewInMemoryRepo()
	for _, task := range tasks {
		repo.tasks[task.Id] = task
	}
	for _, list := range lists {
		repo.lists[list.Id] = list
	}
	return repo
}

func (r *InMemoryRepo) GetLists() ([]entities.List, error) {
	lists := make([]entities.List, 0, len(r.lists))
	for _, list := range r.lists {
		lists = append(lists, list)
	}
	return lists, nil // Nil fulfills the interface, but in this case it's not needed
}

func (r *InMemoryRepo) GetListById(listId string) (entities.List, error) {
	if list, exists := r.lists[listId]; exists {
		return list, nil
	}
	return entities.List{}, fmt.Errorf("List with id %s not found in repository.", listId)
}

func (r *InMemoryRepo) GetTaskById(taskId string) (entities.Task, error) {
	if task, exists := r.tasks[taskId]; exists {
		return task, nil
	}
	return entities.Task{}, fmt.Errorf("Task with id %s not found in repository", taskId)
}

func (r *InMemoryRepo) GetTasksByList(listId string) ([]entities.Task, error) {
	var tasks []entities.Task
	for _, task := range r.tasks {
		if task.ListId == listId {
			tasks = append(tasks, task)
		}
	}
	return tasks, nil // Nil fulfills the interface, but in this case it's not needed
}

func (r *InMemoryRepo) AddTask(task entities.Task) error {
	if _, exists := r.lists[task.ListId]; !exists {
		return fmt.Errorf("List with id %s not found in repository.", task.ListId)
	}
	r.tasks[task.Id] = task
	return nil
}

// Completion in the in memory repository means deleting the task
func (r *InMemoryRepo) CompleteTask(taskId string) error {
	if _, exists := r.tasks[taskId]; !exists {
		return fmt.Errorf("Task with id %s not found in repository.", taskId)
	}
	delete(r.tasks, taskId)
	return nil
}

func (r *InMemoryRepo) UncompleteTask(taskId string) error {
	return fmt.Errorf("Uncomplete task is not implemented yet in the in-memory repository.")
}

func (r *InMemoryRepo) UpdateTask(task entities.Task) (entities.Task, error) {
	if _, exists := r.tasks[task.Id]; !exists {
		return entities.Task{}, fmt.Errorf("Task with id %s not found in repository.", task.Id)
	}
	if _, exists := r.lists[task.ListId]; !exists {
		return entities.Task{}, fmt.Errorf("List with id %s not found in repository.", task.ListId)
	}
	r.tasks[task.Id] = task
	return r.tasks[task.Id], nil
}

func (r *InMemoryRepo) MoveTaskToList(taskId string, targetListId string) error {
	task, exists := r.tasks[taskId]
	if !exists {
		return fmt.Errorf("Task with id %s not found in repository.", taskId)
	}
	if _, exists := r.lists[targetListId]; !exists {
		return fmt.Errorf("Target list with id %s not found in repository.", targetListId)
	}
	task.ListId = targetListId
	r.tasks[taskId] = task
	return nil
}
