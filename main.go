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

	// Run the UI using Bubble Tea
	if err := ui.RunBubbleTeaApp(taskService); err != nil {
		log.Fatalf("Error running Bubble Tea: %v", err)
	}
}
