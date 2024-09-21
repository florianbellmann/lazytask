package cli

import (
	bubbleTeaList "github.com/charmbracelet/bubbles/list"

	"lazytask/application"
	"lazytask/domain"
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
	// Data parts

	lists       []domain.List
	tasks       []domain.Task
	taskService *application.TaskService

	// Input

	// keys         *listKeyMap
	// delegateKeys *delegateKeyMap

	err error // TODO: figure out if this is needed

	// UI List for rendering
	listModel bubbleTeaList.Model
}

func NewModel(taskService *application.TaskService) model {
	// var (
	// 	delegateKeys = newDelegateKeyMap()
	// 	listKeys     = newListKeyMap()
	// )

	uiList := bubbleTeaList.New([]bubbleTeaList.Item{}, bubbleTeaList.NewDefaultDelegate(), 0, 0)
	// delegate := newItemDelegate(delegateKeys)
	// myList := list.New(items, delegate, 0, 0)
	uiList.Title = "Tasks"
	uiList.Styles.Title = titleStyle
	// myList.AdditionalFullHelpKeys = func() []key.Binding {
	// 	return createKeyBindings(listKeys)
	// }

	return model{
		lists:       []domain.List{},
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

	items := []bubbleTeaList.Item{}
	for _, task := range tasks {
		items = append(items, listItem{task: task})
	}
	m.listModel.SetItems(items)
}
