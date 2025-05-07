package cli

import (
	"time"

	bubbleTeaList "github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"

	"lazytask/application"
	"lazytask/entities"
	"lazytask/utils"
)

// Define view modes
type viewMode int

const (
	listMode viewMode = iota // initial value 0
	textInputMode
	dateInputMode
	listChangeMode // Mode for changing task list
)

type listItem struct {
	task entities.Task
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

	// Viewmode determining what to show in the UI
	// TODO: figure out which modes I need when building a real UI
	viewMode viewMode

	// Data parts
	lists []entities.List

	activeList string

	tasks      []entities.Task
	appService application.AppService

	// Temporary storage for operations like changing list
	pendingTask entities.Task

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

func NewUIModel(appService application.AppService) model {
	// var (
	// 	delegateKeys = newDelegateKeyMap()
	// 	listKeys     = newListKeyMap()
	// )

	uiList := bubbleTeaList.New([]bubbleTeaList.Item{}, bubbleTeaList.NewDefaultDelegate(), 0, 0)
	// delegate := newItemDelegate(delegateKeys)
	// my List := list.New(items, delegate, 0, 0)
	uiList.Title = utils.GetConfig().Lists[0]

	uiList.Styles.Title = titleStyle
	// myList.AdditionalFullHelpKeys = func() []key.Binding {
	// 	return createKeyBindings(listKeys)
	// }

	return model{
		viewMode:   listMode,
		lists:      []entities.List{},
		activeList: utils.GetConfig().Lists[0],
		tasks:      []entities.Task{},
		appService: appService,
		listModel:  uiList,

		// delegateKeys: delegateKeys,
	}
}

// Load tasks into the Fancy List
func (m *model) LoadTasks(tasks []entities.Task) {
	items := []bubbleTeaList.Item{}
	for _, task := range tasks {
		// build a time.Time object of today 23:59
		now := time.Now()
		endOfToday := time.Date(now.Year(), now.Month(), now.Day(), 23, 59, 59, 0, now.Location())

		// Filter out tasks that are not due today
		if !task.DueDate.IsZero() && task.DueDate.Before(endOfToday) {
			items = append(items, listItem{task: task})
		}
	}
	m.listModel.SetItems(items)
}
