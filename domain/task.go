package domain

import "time"

// Task represents the core domain task
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
