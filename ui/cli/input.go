package cli

import (
	"lazytask/entities"
	"lazytask/utils"

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
	case "c": // Mark task as completed
		if selectedTask, ok := m.listModel.SelectedItem().(listItem); ok {
			// TODO: check if this worked and then update the ui
			m.appService.CompleteTask(selectedTask.task.Id)

			curr := m.listModel.Index()
			m.listModel.RemoveItem(curr)
		}
	case "a": // add task
		// TODO: add dialog
		m.inputText = textinput.New()
		m.inputText.Placeholder = "Card title"
		m.inputText.Focus()
		m.inputText.CharLimit = 156
		m.inputText.Width = 20

		m.viewMode = textInputMode
		return m, textinput.Blink

		// this is a working first example
		// newTask := entities.Task{
		// 	Title:       "Newtask",
		// 	IsCompleted: false,
		// 	ListId:      config.getConfig().lists[0]
		// 	Priority:    0, // no prio
		// 	Description: "New task description",
		// 	DueDate:     time.Time{}, // no date
		// 	Index:       -1,          // not on the list yet
		// }
		// m.appService.AddTask(newTask)
		// insCmd := m.listModel.InsertItem(-1, listItem{task: newTask})
		// return m, inced

	case "d": // set or change date
		placeholder := m.listModel.SelectedItem().(listItem).task.DueDate

		m.inputText = textinput.New()
		m.inputText.Placeholder = placeholder.UTC().Format("2006-01-02")

		m.inputText.Focus()
		m.inputText.CharLimit = 156
		m.inputText.Width = 20

		m.viewMode = textInputMode
		return m, textinput.Blink
	// TODO: implement
	// https://github.com/EthanEFung/bubble-datepicker

	// return { key: selectedKey, type: ActionType.ChangeDate }

	// case "H":
	// TODO: implement

	// return { key: selectedKey, type: ActionType.DoToday }
	// case "L": // Move to tomorrow
	// log.Printf("KeyPress 'L': Moving task to tomorrow")
	// if selectedTask, ok := m.listModel.SelectedItem().(listItem); ok {
	// 	task := selectedTask.task
	// 	log.Printf("KeyPress 'L': Selected task ID: %s, Title: %s", task.Id, task.Title)
	//
	// 	// Set the due date to tomorrow
	// 	tomorrow := time.Now().AddDate(0, 0, 1)
	//
	// 	// Update only the date part, keep the time if it exists
	// 	if !task.DueDate.IsZero() {
	// 		log.Printf("KeyPress 'L': Original due date: %v", task.DueDate)
	// 		tomorrow = time.Date(
	// 			tomorrow.Year(), tomorrow.Month(), tomorrow.Day(),
	// 			task.DueDate.Hour(), task.DueDate.Minute(), task.DueDate.Second(), 0,
	// 			task.DueDate.Location(),
	// 		)
	// 	}
	//
	// 	task.DueDate = tomorrow
	// 	log.Printf("KeyPress 'L': Setting due date to: %v", tomorrow)
	//
	// 	// Update the task
	// 	log.Printf("KeyPress 'L': Calling UpdateTask")
	// 	err := m.appService.UpdateTask(task)
	// 	if err != nil {
	// 		log.Printf("KeyPress 'L': ERROR updating task: %v", err)
	// 	} else {
	// 		log.Printf("KeyPress 'L': Task successfully updated")
	// 	}
	//
	// 	// Refresh the list view
	// 	log.Printf("KeyPress 'L': Refreshing list view for list: %s", m.activeList)
	// 	m.LoadTasks(m.appService.GetTasksByList(m.activeList))
	// } else {
	// 	log.Printf("KeyPress 'L': No task selected or invalid selection")
	// }
	// return m, nil

	case "e": // change description
		// TODO: implement
		return m, nil

	// return { key: selectedKey, type: ActionType.ChangeDescription }
	case "w": // change list
		if selectedTask, ok := m.listModel.SelectedItem().(listItem); ok {
			task := selectedTask.task

			// Get all available lists for options
			lists := m.appService.GetLists()
			availableListsText := ""
			for i, list := range lists {
				if i > 0 {
					availableListsText += ", "
				}
				availableListsText += list.Id
			}

			// Create input for list selection
			m.inputText = textinput.New()
			m.inputText.Placeholder = "Available: " + availableListsText
			m.inputText.Focus()
			m.inputText.CharLimit = 156
			m.inputText.Width = 30

			// Store metadata in the model for the update function
			// We're using special input mode to signal this is a list change operation
			m.viewMode = listChangeMode

			// Keep reference to the task we're updating
			m.pendingTask = task

			return m, textinput.Blink
		}

	case "r": // rename or change title
		// TODO: implement
		var cmd tea.Cmd
		m.listModel, cmd = m.listModel.Update(msg)
		return m, cmd
	case "u": // undo
		// TODO: implement

		// return { key: selectedKey, type: ActionType.Unarchive }

	case "0":
		// Show all tasks view
		m.activeList = "All"
		allTasks := []entities.Task{}
		lists := m.appService.GetLists()
		for _, list := range lists {
			listTasks := m.appService.GetTasksByList(list.Id)
			allTasks = append(allTasks, listTasks...)
		}
		m.LoadTasks(allTasks)
		m.listModel.Title = "All Tasks"
		return m, nil
	case "1":
		newActiveList := utils.GetConfig().Lists[0]
		m.activeList = newActiveList
		m.LoadTasks(m.appService.GetTasksByList(newActiveList))
		m.listModel.Title = newActiveList
		return m, nil
	case "2":
		newActiveList := utils.GetConfig().Lists[1]
		m.activeList = newActiveList
		m.LoadTasks(m.appService.GetTasksByList(newActiveList))
		m.listModel.Title = newActiveList
		return m, nil
	case "3":
		newActiveList := utils.GetConfig().Lists[2]
		m.activeList = newActiveList
		m.LoadTasks(m.appService.GetTasksByList(newActiveList))
		m.listModel.Title = newActiveList
		return m, nil
	case "4":
		// TODO: add failsafe if not that many lists are present
		newActiveList := utils.GetConfig().Lists[3]
		m.activeList = newActiveList
		m.LoadTasks(m.appService.GetTasksByList(newActiveList))
		m.listModel.Title = newActiveList
		return m, nil
	}

	// Handle navigation within the Fancy List
	var cmd tea.Cmd
	m.listModel, cmd = m.listModel.Update(msg)
	return m, cmd
}
