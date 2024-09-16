package ui

import (
	tea "github.com/charmbracelet/bubbletea"

	"lazytask/domain"
	"lazytask/ui/cli"
	"log"
	"os"
)

type Cli struct{}

func (ui Cli) Show(tasks []domain.Task) {
	tea.SetWindowTitle("Lazytask")

	process := tea.NewProgram(cli.NewModel(tasks), tea.WithAltScreen())

	if _, err := process.Run(); err != nil {
		log.Fatal(err)
		os.Exit(1)
	}
}
