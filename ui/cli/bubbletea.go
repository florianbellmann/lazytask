package cli

import (
	tea "github.com/charmbracelet/bubbletea"
)

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(message tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := message.(type) {
	// We are only handling keyboard inputs
	case tea.KeyMsg:
		return HandleKeyMsg(m, msg)
	}

	return m, nil
}

func (m model) View() string {
	return appStyle.Render(m.list.View())
}
