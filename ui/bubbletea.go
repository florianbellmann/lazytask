package ui

import (
	tea "github.com/charmbracelet/bubbletea"
	"lazytask/application"
)

type CompleteTaskMsg struct {
	taskID string
}

type ErrorMsg struct {
	err error
}

func (m Model) Init() tea.Cmd {
	return nil
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case CompleteTaskMsg:
		// Update the completed task in the Fancy List
		for i, task := range m.tasks {
			if task.Id == msg.taskID {
				m.tasks[i].IsCompleted = true
			}
		}
		m.LoadTasks(m.tasks) // Reload tasks into the list
	case tea.KeyMsg:
		// Handle key presses
		return HandleKeyPress(m, msg)
	case ErrorMsg:
		m.err = msg.err
	}

	return m, nil
}

func (m Model) View() string {
	if m.err != nil {
		return "Error: " + m.err.Error()
	}
	// Use the Fancy List's view for rendering
	return m.listModel.View()
}

func RunBubbleTeaApp(taskService *application.TaskService) error {
	model := NewModel(taskService)
	model.LoadTasks(taskService.GetTasksByList("develop"))
	p := tea.NewProgram(model)

	if err := p.Start(); err != nil {
		return err
	}

	return nil
}
