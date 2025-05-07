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

// TODO: functions...
