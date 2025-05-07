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
	log.Printf("App service initialized")
	return &AppService{
		repo:       repo,
		controller: controller,
	}
}

func (aps *AppService) AddTask(task entities.Task) error {
	if err := aps.controller.AddTask(task); err != nil {
		return err
	}
	return aps.repo.AddTask(task)
}

func (aps *AppService) GetTasksByList(listId string) []entities.Task {
	// TODO: when fetching these i need to make sure to handle errors. I cant cache this.
	tasks := aps.repo.GetTasksByList(listId)
	return tasks
}

func (aps *AppService) GetLists() []entities.List {
	// TODO: when fetching these i need to make sure to init and cache
	lists := aps.repo.GetLists()
	return lists
}

func (aps *AppService) CompleteTask(taskId string) error {
	if err := aps.controller.CompleteTask(taskId); err != nil {
		return err
	}
	return aps.repo.CompleteTask(taskId)
}

func (aps *AppService) UpdateTask(updatedTask entities.Task) error {
	if err := aps.controller.UpdateTask(updatedTask); err != nil {
		return err
	}
	return aps.repo.UpdateTask(updatedTask)
}
