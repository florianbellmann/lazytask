package utils

import (
	"os"
	"strings"
)

// Config holds environment configuration values
type Config struct {
	Lists []string
}

// GetConfig returns the application configuration loaded from environment variables
func GetConfig() Config {
	var config Config

	// Load ignored lists from environment
	if envLists := os.Getenv("LISTS"); envLists != "" {
		config.Lists = strings.Split(envLists, ",")
	} else {
		// Default values
		config.Lists = []string{"develop"}
	}

	return config
}
