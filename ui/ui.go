package ui

import (
	"lazytask/application"
	"lazytask/ui/cli"
	"log"
	"runtime/debug"
)

type Ui struct {
	// Other UI types can be added here
	cli *cli.BubbleTeaApp
}

func NewUi(as application.AppService) *Ui {
	log.Printf("UI initialized.")

	ui := &Ui{
		cli: cli.NewBubbleTeaApp(as),
	}

	return ui
}

func (u *Ui) Run() error {
	if err := u.cli.Run(); err != nil {
		log.Fatalf("Error running CLI: %v", err, debug.Stack())
	}

	return nil
}
