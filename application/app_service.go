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
	log.Printf("App service initialized.")
	return &AppService{
		repo:       repo,
		controller: controller,
	}
}

func (aps *AppService) AddTask(task entities.Task) error {
	return aps.controller.AddTask(task)
}

func (aps *AppService) GetTasksByList(listId string) ([]entities.Task, error) {
	return aps.controller.GetTasksByList(listId)
}

func (aps *AppService) GetLists() ([]entities.List, error) {
	return aps.controller.GetLists()
}

func (aps *AppService) CompleteTask(taskId string) error {
	return aps.controller.CompleteTask(taskId)
}

func (aps *AppService) UpdateTask(updatedTask entities.Task) (entities.Task, error) {
	return aps.controller.UpdateTask(updatedTask)
}
