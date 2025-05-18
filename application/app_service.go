package application

import (
	"lazytask/entities"
	"log"
)

type AppService struct {
	repo       entities.Repository
	controller entities.Controller
}

func NewAppService(repo entities.Repository, controller entities.Controller) *AppService {
	log.Printf("AppService initialized.")
	return &AppService{
		repo:       repo,
		controller: controller,
	}
}

func (aps *AppService) AddTask(task entities.Task) error {
	// Run controller first
	if err := aps.controller.AddTask(task); err != nil {
		return err
	}
	// Sync repository
	if err := aps.repo.AddTask(task); err != nil {
		return err
	}
	return nil
}

func (aps *AppService) GetTasksByList(listID string) ([]entities.Task, error) {
	// Fetch from controller
	tasks, err := aps.controller.GetTasksByList(listID)
	if err != nil {
		return nil, err
	}
	// Sync repository
	if err := aps.repo.SetList(listID, tasks); err != nil {
		return nil, err
	}
	return tasks, nil
}

func (aps *AppService) GetLists() ([]entities.List, error) {
	// Fetch from controller
	lists, err := aps.controller.GetLists()
	if err != nil {
		return nil, err
	}
	// Sync repository
	for _, list := range lists {
		if err := aps.repo.SetList(list.Id, nil); err != nil {
			return nil, err
		}
	}
	return lists, nil
}

func (aps *AppService) CompleteTask(taskID string) error {
	// Run controller first
	if err := aps.controller.CompleteTask(taskID); err != nil {
		return err
	}
	// Sync repository
	if err := aps.repo.CompleteTask(taskID); err != nil {
		return err
	}
	return nil
}

func (aps *AppService) UpdateTask(updatedTask entities.Task) (entities.Task, error) {
	// Run controller first
	task, err := aps.controller.UpdateTask(updatedTask)
	if err != nil {
		return entities.Task{}, err
	}
	// Sync repository
	task, err = aps.repo.UpdateTask(task)
	if err != nil {
		return entities.Task{}, err
	}
	return task, nil
}
