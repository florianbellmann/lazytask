package cli

import (
	"time"

	bubbleTeaList "github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"

	"lazytask/application"
	"lazytask/domain"
)

// Define view modes
type viewMode int

const (
	listMode viewMode = iota // initial value 0
	textInputMode
	dateInputMode
)

type listItem struct {
	task domain.Task
}

func (l listItem) Title() string {
	return l.task.Title
}

func (l listItem) Description() string {
	return l.task.Description
}

func (l listItem) FilterValue() string {
	return l.task.Title
}

type model struct {
	// Cli content
	inputText textinput.Model // TODO: rename me

	mode viewMode

	// Data parts
	lists []domain.List

	activeList string

	tasks       []domain.Task
	taskService *application.TaskService

	// Input

	// keys         *listKeyMap
	// delegateKeys *delegateKeyMap

	err error // TODO: figure out if this is needed

	// UI List for rendering
	listModel bubbleTeaList.Model
}

func TextInputInit() tea.Cmd {
	return textinput.Blink
}

func NewModel(taskService *application.TaskService) model {
	// var (
	// 	delegateKeys = newDelegateKeyMap()
	// 	listKeys     = newListKeyMap()
	// )

	uiList := bubbleTeaList.New([]bubbleTeaList.Item{}, bubbleTeaList.NewDefaultDelegate(), 0, 0)
	// delegate := newItemDelegate(delegateKeys)
	// myList := list.New(items, delegate, 0, 0)
	uiList.Title = "develop"

	uiList.Styles.Title = titleStyle
	// myList.AdditionalFullHelpKeys = func() []key.Binding {
	// 	return createKeyBindings(listKeys)
	// }

	return model{
		mode:        listMode,
		lists:       []domain.List{},
		activeList:  "develop",
		tasks:       []domain.Task{},
		taskService: taskService,
		listModel:   uiList,

		// delegateKeys: delegateKeys,
	}
}

// Load tasks into the Fancy List
func (m *model) LoadTasks(tasks []domain.Task) {
	// items := make([]list.Item, len(tasks))
	// for i := 0; i < len(tasks); i++ {
	// 	log.Printf("Task: %v", tasks[i].Title)
	// 	items[i] = listItem{title: tasks[i].Title + " | " + tasks[i].DueDate.String() + " | " + tasks[i].List, desc: tasks[i].Description}
	// }

	// log.Printf("Items: %v", items)

	// TODO: load only overdue tasks. how does this work with the indexes?

	items := []bubbleTeaList.Item{}
	for _, task := range tasks {
		// build a time.Time object of today 23:59
		now := time.Now()
		endOfToday := time.Date(now.Year(), now.Month(), now.Day(), 23, 59, 59, 0, now.Location())
		if !task.DueDate.IsZero() && task.DueDate.Before(endOfToday) {
			items = append(items, listItem{task: task})
		}
	}
	m.listModel.SetItems(items)
}
