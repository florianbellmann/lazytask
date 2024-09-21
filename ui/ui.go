package ui

import (
	"lazytask/application"
	"lazytask/ui/cli"
)

func NewCli(ts application.TaskService) *cli.BubbleTeaApp {
	return cli.NewBubbleTeaApp(ts)
}

// Other UI types can be added here
