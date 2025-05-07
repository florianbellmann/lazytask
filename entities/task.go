package entities

import "time"

// Task represents the core entities task
type Task struct {
	DueDate     time.Time
	Id          string
	IsCompleted bool
	ListId      string
	Description string
	Priority    int
	Title       string
	Index       int
}
