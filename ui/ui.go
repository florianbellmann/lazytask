package ui

import (
	"fmt"
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
		return fmt.Errorf("Error running CLI: %v", err)
	}

	return nil
}
