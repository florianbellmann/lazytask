package ui

import (
	"fmt"
	tea "github.com/charmbracelet/bubbletea"
	// "github.com/charmbracelet/lipgloss"
	"lazytask/domain"
	"log"
)

// Bubbletea

type model int

func (m model) Init() tea.Cmd {
	// p := tea.NewProgram(model(5), tea.WithAltScreen())
	// if _, err := p.Run(); err != nil {
	// 	log.Fatal(err)
	// }
	//
	// tea.SetWindowTitle("Lazytask")
	return nil
}

// TODO:
// fancy list
// text input
// text area
// exec

func (m model) Update(message tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := message.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "esc", "ctrl+c":
			return m, tea.Quit
		}
	}

	return m, nil
}

func (m model) View() string {
	return fmt.Sprintf("Hello")
}

// Cli

type Cli struct{}

func (ui Cli) Init() {
	tea.SetWindowTitle("Lazytask")
	p := tea.NewProgram(model(5), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		log.Fatal(err)
	}

	// model.Init()
}

func (ui Cli) ShowTasks(tasks []domain.Task) {}
