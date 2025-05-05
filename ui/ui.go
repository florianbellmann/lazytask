package ui

import (
	"lazytask/application"
	"lazytask/domain"
	"lazytask/ui/cli"
)

type Ui struct {
	// Other UI types can be added here
	cli *cli.BubbleTeaApp
}

func NewCli(ts application.TaskService) domain.Ui {
	return &Ui{cli: cli.NewBubbleTeaApp(ts)}
}

func (u *Ui) Init() error {
	// Initialize the UI
	// This could include setting up the terminal, loading resources, etc.
	return nil
}

func (u *Ui) Run() error {
	// Run the UI
	// This could include starting the main loop, handling events, etc.
	return u.cli.Run()
}
