package main

import (
	"lazytask/application"
	"lazytask/infrastructure"
	"lazytask/ui"
	"log"
)

func main() {
	// Set up the reminder task controller
	reminderCtrl := infrastructure.NewReminderTaskController()

	// Create the application service
	taskService := application.NewTaskService(reminderCtrl)

	log.Printf("Starting LazyTask...")
	// Initialize the UI
	ui := ui.NewCli(*taskService)

	// Run the UI
	if err := ui.Run(); err != nil {
		log.Fatalf("Error running UI: %v", err)
	}
}
