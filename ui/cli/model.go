package cli

import (
	"log"

	key "github.com/charmbracelet/bubbles/key"
	list "github.com/charmbracelet/bubbles/list"

	"lazytask/domain"
)

type listItem struct {
	title string
	desc  string
}

func (i listItem) Title() string       { return i.title }
func (i listItem) Description() string { return i.desc }
func (i listItem) FilterValue() string { return i.title }

type model struct {
	list         list.Model
	keys         *listKeyMap
	delegateKeys *delegateKeyMap
}

func NewModel(tasks []domain.Task) model {
	var (
		delegateKeys = newDelegateKeyMap()
		listKeys     = newListKeyMap()
	)

	items := make([]list.Item, len(tasks))
	for i := 0; i < len(tasks); i++ {
		log.Printf("Task: %v", tasks[i].Title)
		items[i] = listItem{title: tasks[i].Title, desc: tasks[i].Notes}
		// items[i] = list.Item{title: tasks[i].Title}
	}

	// log.Printf("Items: %v", items)

	// Setup list
	delegate := newItemDelegate(delegateKeys)
	myList := list.New(items, delegate, 0, 0)
	// myList := list.New(items, list.NewDefaultDelegate(), 0, 0)
	myList.Title = "My List"
	myList.Styles.Title = titleStyle
	myList.AdditionalFullHelpKeys = func() []key.Binding {
		return createKeyBindings(listKeys)
	}

	return model{
		list:         myList,
		keys:         listKeys,
		delegateKeys: delegateKeys,
	}
}
