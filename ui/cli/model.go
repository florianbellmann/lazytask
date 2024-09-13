package cli

import (
	key "github.com/charmbracelet/bubbles/key"
	list "github.com/charmbracelet/bubbles/list"

	"lazytask/domain"
)

type ListItem struct {
	task domain.Task
}

func (i ListItem) FilterValue() string { return i.task.Title }

type model struct {
	list         list.Model
	keys         *listKeyMap
	delegateKeys *delegateKeyMap
}

func NewModel(tasks []domain.Task) model {
	var (
		delegateKeys = newDelegateKeyMap()
		listKeys     = NewListKeyMap()
	)

	items := make([]list.Item, len(tasks))
	for i := 0; i < len(tasks); i++ {
		items[i] = ListItem{task: tasks[i]}
	}

	// Setup list
	delegate := newItemDelegate(delegateKeys)
	myList := list.New(items, delegate, 0, 0)
	myList.Title = "My List"
	myList.Styles.Title = titleStyle
	myList.AdditionalFullHelpKeys = func() []key.Binding {
		return CreateKeyBindings(listKeys)
	}

	return model{
		list:         myList,
		keys:         listKeys,
		delegateKeys: delegateKeys,
	}
}
