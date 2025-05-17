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

func (r *InMemoryRepo) GetLists() []entities.List {
	lists := make([]entities.List, 0, len(r.lists))
	for _, list := range r.lists {
		lists = append(lists, list)
	}
	return lists
}

func (r *InMemoryRepo) GetListById(listId string) (entities.List, error) {
	if list, exists := r.lists[listId]; exists {
		return list, nil
	}
	return entities.List{}, fmt.Errorf("list with id %s not found", listId)
}

func (r *InMemoryRepo) GetTaskById(taskId string) (entities.Task, error) {
	if task, exists := r.tasks[taskId]; exists {
		return task, nil
	}
	return entities.Task{}, fmt.Errorf("task with id %s not found", taskId)
}

func (r *InMemoryRepo) GetTasksByList(listId string) []entities.Task {
	var tasks []entities.Task
	for _, task := range r.tasks {
		if task.ListId == listId {
			tasks = append(tasks, task)
		}
	}
	return tasks
}

func (r *InMemoryRepo) AddTask(task entities.Task) error {
	if _, exists := r.lists[task.ListId]; !exists {
		return fmt.Errorf("list with id %s not found", task.ListId)
	}
	r.tasks[task.Id] = task
	return nil
}

// Completion in the in memory repository means deleting the task
func (r *InMemoryRepo) CompleteTask(taskId string) error {
	if _, exists := r.tasks[taskId]; !exists {
		return fmt.Errorf("task with id %s not found", taskId)
	}
	delete(r.tasks, taskId)
	return nil
}

func (r *InMemoryRepo) UncompleteTask(taskId string) error {
	// TODO: implement uncomplete task
	return errors.New("Not implemented")
}

func (r *InMemoryRepo) UpdateTask(task entities.Task) error {
	if _, exists := r.tasks[task.Id]; !exists {
		return fmt.Errorf("task with id %s not found", task.Id)
	}
	if _, exists := r.lists[task.ListId]; !exists {
		return fmt.Errorf("list with id %s not found", task.ListId)
	}
	r.tasks[task.Id] = task
	return nil
}

func (r *InMemoryRepo) MoveTaskToList(taskId string, targetListId string) error {
	task, exists := r.tasks[taskId]
	if !exists {
		return fmt.Errorf("task with id %s not found", taskId)
	}
	if _, exists := r.lists[targetListId]; !exists {
		return fmt.Errorf("target list with id %s not found", targetListId)
	}
	task.ListId = targetListId
	r.tasks[taskId] = task
	return nil
}
