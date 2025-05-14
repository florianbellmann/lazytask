package utils

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"
)

func InitLogging() {
	_, err := setupLogFiles()
	if err != nil {
		fmt.Printf("Error setting up logging: %v\n", err)
		// Continue with console logging
	}
	// We don't store or close the file pointer to keep logging active
}

// setupLogFiles configures logging to write to a file
func setupLogFiles() (*os.File, error) {
	// Create logs directory if it doesn't exist
	logsDir := "logs"
	if err := os.MkdirAll(logsDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create logs directory: %w", err)
	}

	// Create a new log file with timestamp
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	logFileName := "lazytask_" + timestamp + ".log"
	logFileNameInclPath := filepath.Join(logsDir, logFileName)

	logFile, err := os.OpenFile(logFileNameInclPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
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

	log.Printf("Logging initialized - writing to %s", logFileNameInclPath)

	return logFile, nil
}
