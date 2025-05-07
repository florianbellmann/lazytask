package main

import (
	"lazytask/application"
	ctrl "lazytask/infrastructure/controller"
	repo "lazytask/infrastructure/repository"
	"lazytask/ui"
	"lazytask/utils"
	"log"
)

func main() {
	// Read configs
	appConfig := utils.GetConfig()
	log.Printf("Configuration loaded - Lists: %v", appConfig.Lists)
	// Set up logging
	utils.InitLogging()
	log.Printf("=== LazyTask Starting ===")

	// Set up the application with DI
	reminderCtrl := ctrl.NewReminderTaskController()
	inMemoryRepository := repo.NewInMemoryRepo()
	appService := application.NewAppService(reminderCtrl, inMemoryRepository)

	// Run the UI
	ui := ui.NewCli(*appService)
	if err := ui.Run(); err != nil {
		log.Fatalf("Error running UI: %v", err)
	}
}
