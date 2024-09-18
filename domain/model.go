package domain

import (
	"time"
)

type List struct {
	Id string
}

type Task struct {
	DueDate     time.Time
	Id          string
	IsCompleted bool
	ListId      string
	Notes       string
	Priority    int
	Title       string
	Index       int
}
