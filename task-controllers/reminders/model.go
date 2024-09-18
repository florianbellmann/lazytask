package reminders

import (
	"lazytask/domain"
	"time"
)

type ReminderList = string

func ReminderListToList(rl ReminderList) domain.List {
	return domain.List{Id: string(rl)}
}

func ListToReminderList(l domain.List) ReminderList {
	return ReminderList(l.Id)
}

type Reminder struct {
	CreationDate time.Time    `json:"creationDate"`
	DueDate      time.Time    `json:"dueDate"`
	ExternalID   string       `json:"externalId"`
	IsCompleted  bool         `json:"isCompleted"`
	LastModified time.Time    `json:"lastModified"`
	List         ReminderList `json:"list"`
	Notes        string       `json:"notes"`
	Priority     int          `json:"priority"`
	Title        string       `json:"title"`
}

func (rem Reminder) ToTask() domain.Task {
	return domain.Task{
		DueDate:     rem.DueDate,
		Id:          rem.ExternalID,
		IsCompleted: rem.IsCompleted,
		List:        rem.List,
		Notes:       rem.Notes,
		Priority:    rem.Priority,
		Title:       rem.Title,
		Index:       rem.Index,
	}
}

func TaskToReminder(t domain.Task) Reminder {
	return Reminder{
		CreationDate: time.Now(),
		DueDate:      t.DueDate,
		ExternalID:   t.Id,
		IsCompleted:  t.IsCompleted,
		LastModified: time.Now(),
		List:         t.List,
		Notes:        t.Notes,
		Priority:     t.Priority,
		Title:        t.Title,
	}
}
