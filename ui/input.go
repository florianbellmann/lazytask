package ui

import (
	tea "github.com/charmbracelet/bubbletea"
	"lazytask/application"
)

func HandleKeyPress(m Model, msg tea.KeyMsg) (Model, tea.Cmd) {
	switch msg.String() {
	case "enter":
		if selectedTask, ok := m.listModel.SelectedItem().(taskItem); ok {
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
