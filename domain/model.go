package domain

import (
	"time"
)

type List = string

type Task struct {
	CreationDate time.Time `json:"creationDate"`
	DueDate      time.Time `json:"dueDate"`
	ExternalID   string    `json:"externalId"`
	IsCompleted  bool      `json:"isCompleted"`
	LastModified time.Time `json:"lastModified"`
	List         string    `json:"list"`
	Priority     int       `json:"priority"`
	Title        string    `json:"title"`
}
