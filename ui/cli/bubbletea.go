package cli

import (
	"fmt"
	"lazytask/application"
	"lazytask/config"
	"lazytask/domain"
	"log"
	"os"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

// TODO: is this used?
type (
	errMsg error
)

type BubbleTeaApp struct {
	taskService application.TaskService
}

func NewBubbleTeaApp(ts application.TaskService) *BubbleTeaApp {
	return &BubbleTeaApp{taskService: ts}

}

func (m model) Init() tea.Cmd {
	// switch m.mode {
	// case listMode:
	// 	return nil
	// case textInputMode:
	// 	return TextInputInit()
	// }
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch m.mode {
	case listMode:
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

	case textInputMode:
		var cmd tea.Cmd

		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.Type {
			case tea.KeyCtrlC, tea.KeyEsc:
				m.inputText.Reset()
				m.mode = listMode
				return m, nil

			case tea.KeyEnter:
				value := m.inputText.Value()
				m.inputText.Reset()
				m.mode = listMode

				newTask := domain.Task{
					Title:       value,
					IsCompleted: false,
					DueDate:     time.Now(),
					ListId:      config.GetConfig().Lists[0],
					Priority:    0, // no prio
					// Description: "New task description",
					// DueDate: time.Time{}, // no date
					Index: -1, // not on the list yet
				}
				m.taskService.AddTask(newTask)
				insCmd := m.listModel.InsertItem(-1, listItem{task: newTask})

				return m, insCmd

			}

		// We handle errors just like any other message
		case errMsg:
			m.err = msg
			return m, nil
		}

		m.inputText, cmd = m.inputText.Update(msg)
		return m, cmd

	case dateInputMode:
		var cmd tea.Cmd

		switch msg := msg.(type) {
		case tea.KeyMsg:
			switch msg.Type {
			case tea.KeyCtrlC, tea.KeyEsc:
				m.inputText.Reset()
				m.mode = listMode
				return m, nil

			case tea.KeyEnter:
				// value := m.inputText.Value()
				m.inputText.Reset()
				m.mode = listMode

				// TODO: implementation of card editing missing in reminders-cli
				// newTask := domain.Task{
				// 	Title:       value,
				// 	IsCompleted: false,
				// 	ListId:      config.GetConfig().lists[0],
				// 	Priority:    0, // no prio
				// 	// Description: "New task description",
				// 	// DueDate: time.Time{}, // no date
				// 	Index: -1, // not on the list yet
				// }
				// m.taskService.AddTask(newTask)
				// insCmd := m.listModel.InsertItem(-1, listItem{task: newTask})

				// return m, insCmd
				return m, nil

			}

		// We handle errors just like any other message
		case errMsg:
			m.err = msg
			return m, nil
		}

		m.inputText, cmd = m.inputText.Update(msg)
		return m, cmd

	}
	return m, nil
}

func (m model) View() string {
	if m.err != nil {
		return "Error: " + m.err.Error()
	}

	switch m.mode {
	case listMode:
		// return m.listView.View()
		return appStyle.Render(m.listModel.View())
	case textInputMode:

		return fmt.Sprintf(
			"Insert new card\n\n%s\n\n%s",
			m.inputText.View(),
			"(esc to quit)",
		) + "\n"

	case dateInputMode:
		return fmt.Sprintf(
			"Insert new card due date\n\n%s\n\n%s",
			m.inputText.View(),
			"(esc to quit)",
		) + "\n"
	}
	return ""
}

func (b BubbleTeaApp) Run() error {
	model := NewModel(&b.taskService)
	model.LoadTasks(b.taskService.GetTasksByList(config.GetConfig().Lists[0]))
	process := tea.NewProgram(model, tea.WithAltScreen())

	if _, err := process.Run(); err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	return nil
}
