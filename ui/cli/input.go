package cli

import (
	"lazytask/application"
	"lazytask/domain"
	"log"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
)

type CompleteTaskMsg struct {
	taskID string
}

type ErrorMsg struct {
	err error
}

func HandleKeyPress(m model, msg tea.KeyMsg) (model, tea.Cmd) {
	switch msg.String() {
	case "c":
		if selectedTask, ok := m.listModel.SelectedItem().(listItem); ok {
			taskID := selectedTask.task.Id
			// m.listModel.Paginator.
			curr := m.listModel.Index()
			m.listModel.RemoveItem(curr)
			// return m, completeTask(m.taskService, taskID)
			completeTask(m.taskService, taskID)
		}
	case "a":

		m.inputText = textinput.New()
		m.inputText.Placeholder = "Card title"
		m.inputText.Focus()
		m.inputText.CharLimit = 156
		m.inputText.Width = 20

		m.mode = textInputMode
		return m, textinput.Blink

		// this is a working first example
		// newTask := domain.Task{
		// 	Title:       "Newtask",
		// 	IsCompleted: false,
		// 	ListId:      "develop",
		// 	Priority:    0, // no prio
		// 	Description: "New task description",
		// 	DueDate:     time.Time{}, // no date
		// 	Index:       -1,          // not on the list yet
		// }
		// m.taskService.AddTask(newTask)
		// insCmd := m.listModel.InsertItem(-1, listItem{task: newTask})
		// return m, inced

	case "d":

		placeholder := m.listModel.SelectedItem().(listItem).task.DueDate

		m.inputText = textinput.New()
		m.inputText.Placeholder = placeholder.UTC().Format("2006-01-02")

		m.inputText.Focus()
		m.inputText.CharLimit = 156
		m.inputText.Width = 20

		m.mode = textInputMode
		return m, textinput.Blink
	// TODO: implement
	// https://github.com/EthanEFung/bubble-datepicker

	// return { key: selectedKey, type: ActionType.ChangeDate }

	case "H":
	// TODO: implement

	// return { key: selectedKey, type: ActionType.DoToday }
	case "L":
		log.Printf("KeyPress 'L': Moving task to tomorrow")
		if selectedTask, ok := m.listModel.SelectedItem().(listItem); ok {
			task := selectedTask.task
			log.Printf("KeyPress 'L': Selected task ID: %s, Title: %s", task.Id, task.Title)
			
			// Set the due date to tomorrow
			tomorrow := time.Now().AddDate(0, 0, 1)
			
			// Update only the date part, keep the time if it exists
			if !task.DueDate.IsZero() {
				log.Printf("KeyPress 'L': Original due date: %v", task.DueDate)
				tomorrow = time.Date(
					tomorrow.Year(), tomorrow.Month(), tomorrow.Day(), 
					task.DueDate.Hour(), task.DueDate.Minute(), task.DueDate.Second(), 0,
					task.DueDate.Location(),
				)
			}
			
			task.DueDate = tomorrow
			log.Printf("KeyPress 'L': Setting due date to: %v", tomorrow)
			
			// Update the task
			log.Printf("KeyPress 'L': Calling UpdateTask")
			err := m.taskService.UpdateTask(task)
			if err != nil {
				log.Printf("KeyPress 'L': ERROR updating task: %v", err)
			} else {
				log.Printf("KeyPress 'L': Task successfully updated")
			}
			
			// Refresh the list view
			log.Printf("KeyPress 'L': Refreshing list view for list: %s", m.activeList)
			m.LoadTasks(m.taskService.GetTasksByList(m.activeList))
		} else {
			log.Printf("KeyPress 'L': No task selected or invalid selection")
		}
		return m, nil
	case "t":
	// TODO: implement

	// return { key: selectedKey, type: ActionType.ChangeTitle }
	case "e":
	// TODO: implement

	// return { key: selectedKey, type: ActionType.ChangeDescription }
	case "o":
		// TODO: implement

		// return { key: selectedKey, type: ActionType.AddLabel } or tag

	case "r":
		// TODO: is this redundant?
		var cmd tea.Cmd
		m.listModel, cmd = m.listModel.Update(msg)
		return m, cmd
	case "u":
		// TODO: implement

		// return { key: selectedKey, type: ActionType.Unarchive }

	case "1":
		m.activeList = "Priv"
		m.LoadTasks(m.taskService.GetTasksByList("Priv"))
		m.listModel.Title = "Priv"
		return m, nil
	case "2":
		m.activeList = "Work"
		m.LoadTasks(m.taskService.GetTasksByList("Work"))
		m.listModel.Title = "Work"
		return m, nil
	case "3":
		m.activeList = "Flisa"
		m.LoadTasks(m.taskService.GetTasksByList("Flisa"))
		m.listModel.Title = "Flisa"
		return m, nil

	}

	// Handle navigation within the Fancy List
	var cmd tea.Cmd
	m.listModel, cmd = m.listModel.Update(msg)
	return m, cmd
}

// func completeTask(service *application.TaskService, taskId string) tea.Cmd {
func completeTask(service *application.TaskService, taskId string) {
	// return func() tea.Msg {
	// err := service.CompleteTask(taskId)
	service.CompleteTask(taskId)
	// if err != nil {
	// return ErrorMsg{err: err}
	// }
	// return CompleteTaskMsg{taskID: taskId}
	// }
}

// Helper function for updating a task
func updateTask(service *application.TaskService, task domain.Task) {
	service.UpdateTask(task)
}