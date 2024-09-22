package cli

import (
	tea "github.com/charmbracelet/bubbletea"
	"lazytask/application"
	"log"
	"os"
)

type BubbleTeaApp struct {
	taskService application.TaskService
}

func NewBubbleTeaApp(ts application.TaskService) *BubbleTeaApp {
	return &BubbleTeaApp{taskService: ts}

}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case CompleteTaskMsg:
		// h, v := appStyle.GetFrameSize()
		// m.listModel.SetSize(msg.Width-h, msg.Height-v)

		// Update the completed task in the Fancy List
		for i, task := range m.tasks {
			if task.Id == msg.taskID {
				m.tasks[i].IsCompleted = true
			}
		}

		m.LoadTasks(m.tasks) // Reload tasks into the list

	case tea.WindowSizeMsg:
		h, v := appStyle.GetFrameSize()
		m.listModel.SetSize(msg.Width-h, msg.Height-v)

	case ErrorMsg:
		m.err = msg.err

	case tea.KeyMsg:
		// // TODO: move this to input as well
		// // Don't match any of the keys below if we're actively filtering.
		// if m.list.FilterState() == list.Filtering {
		// 	break
		// }
		//
		// handleKeyMsg(m, msg)

		// Handle key presses
		return HandleKeyPress(m, msg)

	}

	// This will also call our delegate's update function.
	newListModel, cmd := m.listModel.Update(msg)
	m.listModel = newListModel
	cmds = append(cmds, cmd)

	return m, tea.Batch(cmds...)

}

func (m model) View() string {
	if m.err != nil {
		return "Error: " + m.err.Error()
	}

	return appStyle.Render(m.listModel.View())
}

func (b BubbleTeaApp) Run() error {
	model := NewModel(&b.taskService)
	model.LoadTasks(b.taskService.GetTasksByList("develop"))
	process := tea.NewProgram(model, tea.WithAltScreen())

	if _, err := process.Run(); err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	return nil
}
