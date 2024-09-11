package ui

import (
	// tea "github.com/charmbracelet/bubbletea"
	// "github.com/charmbracelet/lipgloss"
	"lazytask/domain"
)

type Cli struct{}

func (t Cli) ShowTasks(tasks []domain.Task) {
}

// var (
// 	appStyle = lipgloss.NewStyle().Padding(1, 2)
//
// 	titleStyle = lipgloss.NewStyle().
// 			Foreground(lipgloss.Color("#FFFDF5")).
// 			Background(lipgloss.Color("#25A065")).
// 			Padding(0, 1)
//
// 	statusMessageStyle = lipgloss.NewStyle().
// 				Foreground(lipgloss.AdaptiveColor{Light: "#04B575", Dark: "#04B575"}).
// 				Render
// )

// type model int

// type tickMsg time.Time

// main
// p := tea.NewProgram(model(5), tea.WithAltScreen())
// if _, err := p.Run(); err != nil {
// 	log.Fatal(err)
// }
//
// func (m model) Init() tea.Cmd {
// 	tea.SetWindowTitle("Lazytask")
// 	return tick()
// }
//
// // TODO:
// // fancy list
// // text input
// // text area
// // exec
//
// func (m model) Update(message tea.Msg) (tea.Model, tea.Cmd) {
// 	switch msg := message.(type) {
// 	case tea.KeyMsg:
// 		switch msg.String() {
// 		case "q", "esc", "ctrl+c":
// 			return m, tea.Quit
// 		}
//
// 	case tickMsg:
// 		m--
// 		if m <= 0 {
// 			return m, tea.Quit
// 		}
// 		return m, tick()
// 	}
//
// 	return m, nil
// }
//
// func (m model) View() string {
// 	return fmt.Sprintf("\n\n     Hi. This program will exit in %d seconds...", m)
// }
//
// func tick() tea.Cmd {
// 	return tea.Tick(time.Second, func(t time.Time) tea.Msg {
// 		return tickMsg(t)
// 	})
// }
