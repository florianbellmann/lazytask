package cli

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

func HandleKeyPress(m model, msg tea.KeyMsg) (model, tea.Cmd) {
	switch msg.String() {
	case "enter":
		if selectedTask, ok := m.listModel.SelectedItem().(listItem); ok {
			taskID := selectedTask.task.Id
			return m, completeTask(m.taskService, taskID)
		}
	}

	// Handle navigation within the Fancy List
	var cmd tea.Cmd
	m.listModel, cmd = m.listModel.Update(msg)
	return m, cmd
}

func completeTask(service *application.TaskService, taskId string) tea.Cmd {
	return func() tea.Msg {
		err := service.CompleteTask(taskId)
		if err != nil {
			return ErrorMsg{err: err}
		}
		return CompleteTaskMsg{taskID: taskId}
	}
}
