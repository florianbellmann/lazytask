package cli

import (
	"fmt"
	"lazytask/application"
	"lazytask/entities"
	"lazytask/utils"
	"log"
	"os"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

// TODO: check usage
type (
	errMsg error
)

type BubbleTeaApp struct {
	appService application.AppService
}

func NewBubbleTeaApp(ts application.AppService) *BubbleTeaApp {
	return &BubbleTeaApp{appService: ts}

}

func (m model) Init() tea.Cmd {
	return nil
}

// Run the whole UI CLI application
func (b BubbleTeaApp) Run() error {
	model := NewUIModel(b.appService)
	ts, err := b.appService.GetTasksByList(utils.GetConfig().Lists[0])
	if err != nil {
		return fmt.Errorf("error getting tasks: %w", err)
	}

	model.LoadTasks(ts)

	process := tea.NewProgram(model, tea.WithAltScreen())

	if _, err := process.Run(); err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch m.viewMode {
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
				m.viewMode = listMode
				return m, nil

			case tea.KeyEnter:
				value := m.inputText.Value()
				m.inputText.Reset()
				m.viewMode = listMode

				newTask := entities.Task{
					Title:       value,
					IsCompleted: false,
					DueDate:     time.Now(),
					ListId:      utils.GetConfig().Lists[0],
					Priority:    0, // no prio
					// Description: "New task description",
					// DueDate: time.Time{}, // no date
					Index: -1, // not on the list yet
				}
				m.appService.AddTask(newTask)
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
				m.viewMode = listMode
				return m, nil

			case tea.KeyEnter:
				// value := m.inputText.Value()
				m.inputText.Reset()
				m.viewMode = listMode

				// TODO: implementation of card editing missing in reminders-cli
				// newTask := entities.Task{
				// 	Title:       value,
				// 	IsCompleted: false,
				// 	ListId:      config.GetConfig().lists[0],
				// 	Priority:    0, // no prio
				// 	// Description: "New task description",
				// 	// DueDate: time.Time{}, // no date
				// 	Index: -1, // not on the list yet
				// }
				// m.appService.AddTask(newTask)
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

// Main function of a bubble tea app, determining what to show
func (m model) View() string {
	if m.err != nil {
		// TODO: return error isntead
		log.Printf("Error: %v", m.err)
		return "Error: " + m.err.Error()
	}

	switch m.viewMode {
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
