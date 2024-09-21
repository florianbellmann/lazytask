package cli

import "github.com/charmbracelet/lipgloss"

var (
	descriptionStyle = lipgloss.NewStyle().Italic(true).Foreground(lipgloss.Color("#FF00FF"))

	appStyle = lipgloss.NewStyle().Padding(1, 2)

	titleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FFFDF5")).
			Background(lipgloss.Color("#25A065")).
			Padding(0, 1)

	statusMessageStyle = lipgloss.NewStyle().
				Foreground(lipgloss.AdaptiveColor{Light: "#04B575", Dark: "#04B575"}).
				Render
)
