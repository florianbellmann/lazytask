package main

import (
	"fmt"
	"lazytask/application"
	"lazytask/infrastructure"
	"lazytask/ui"
	"log"
	"os"
	"path/filepath"
	"time"
)

// setupLogging configures logging to write to a file
func setupLogging() (*os.File, error) {
	// Create logs directory if it doesn't exist
	logsDir := "logs"
	if err := os.MkdirAll(logsDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create logs directory: %w", err)
	}

	// Create a new log file with timestamp
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	logFileName := filepath.Join(logsDir, "lazytask_"+timestamp+".log")
	
	logFile, err := os.OpenFile(logFileName, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to open log file: %w", err)
	}

	// Set the logger output to the file
	log.SetOutput(logFile)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	
	// Create a symbolic link to the most recent log file for easy access
	latestLogLink := filepath.Join(logsDir, "latest.log")
	_ = os.Remove(latestLogLink) // Remove existing symlink if it exists
	_ = os.Symlink(logFileName, latestLogLink)
	
	log.Printf("Logging initialized - writing to %s", logFileName)
	
	return logFile, nil
}

func main() {
	// Set up logging
	logFile, err := setupLogging()
	if err != nil {
		fmt.Printf("Error setting up logging: %v\n", err)
		// Continue with console logging
	} else {
		defer logFile.Close()
	}
	
	log.Printf("=== LazyTask Starting ===")
	
	// Set up the reminder task controller
	reminderCtrl := infrastructure.NewReminderTaskController()
	log.Printf("Reminder controller initialized")

	// Create the application service
	taskService := application.NewTaskService(reminderCtrl)
	log.Printf("Task service initialized")

	// Initialize the UI
	ui := ui.NewCli(*taskService)
	log.Printf("UI initialized, starting application...")

	// Run the UI
	if err := ui.Run(); err != nil {
		log.Fatalf("Error running UI: %v", err)
	}
}
