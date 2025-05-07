package ui

import (
	"lazytask/application"
	"lazytask/ui/cli"
	"log"
)

type Ui struct {
	// Other UI types can be added here
	cli *cli.BubbleTeaApp
}

func NewCli(as application.AppService) *cli.BubbleTeaApp {
	log.Printf("Initializing UI...")
	return cli.NewBubbleTeaApp(as)
}

func (u *Ui) Run() error {
	if err := u.cli.Run(); err != nil {
		log.Fatalf("Error running CLI: %v", err)
	}

	return nil
}
