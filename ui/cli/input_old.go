package cli

//
// import (
// 	"lazytask/entities"
//
// 	key "github.com/charmbracelet/bubbles/key"
// 	list "github.com/charmbracelet/bubbles/list"
// 	tea "github.com/charmbracelet/bubbletea"
// )
//
// // TODO:
// // https://chatgpt.com/c/66e43e4f-0c20-800c-b867-c498218cd040
//
// type listKeyMap struct {
// 	toggleSpinner    key.Binding
// 	toggleTitleBar   key.Binding
// 	toggleStatusBar  key.Binding
// 	togglePagination key.Binding
// 	toggleHelpMenu   key.Binding
// 	insertItem       key.Binding
// }
//
// func newListKeyMap() *listKeyMap {
// 	return &listKeyMap{
// 		insertItem: key.NewBinding(
// 			key.WithKeys("a"),
// 			key.WithHelp("a", "add item"),
// 		),
// 		toggleSpinner: key.NewBinding(
// 			key.WithKeys("s"),
// 			key.WithHelp("s", "toggle spinner"),
// 		),
// 		toggleTitleBar: key.NewBinding(
// 			key.WithKeys("T"),
// 			key.WithHelp("T", "toggle title"),
// 		),
// 		toggleStatusBar: key.NewBinding(
// 			key.WithKeys("S"),
// 			key.WithHelp("S", "toggle status"),
// 		),
// 		togglePagination: key.NewBinding(
// 			key.WithKeys("P"),
// 			key.WithHelp("P", "toggle pagination"),
// 		),
// 		toggleHelpMenu: key.NewBinding(
// 			key.WithKeys("H"),
// 			key.WithHelp("H", "toggle help"),
// 		),
// 	}
// }
//
// func newItemDelegate(keys *delegateKeyMap) list.DefaultDelegate {
// 	d := list.NewDefaultDelegate()
//
// 	d.UpdateFunc = func(msg tea.Msg, m *list.Model) tea.Cmd {
// 		var title string
//
// 		if i, ok := m.SelectedItem().(listItem); ok {
// 			title = i.title
// 			// title = i.task.Title
// 		} else {
// 			return nil
// 		}
//
// 		switch msg := msg.(type) {
// 		case tea.KeyMsg:
// 			switch {
// 			case key.Matches(msg, keys.choose):
// 				return m.NewStatusMessage(statusMessageStyle("You chose " + title))
//
// 			case key.Matches(msg, keys.remove):
// 				index := m.Index()
// 				m.RemoveItem(index)
// 				if len(m.Items()) == 0 {
// 					keys.remove.SetEnabled(false)
// 				}
// 				return m.NewStatusMessage(statusMessageStyle("Deleted " + title))
// 			}
// 		}
//
// 		return nil
// 	}
//
// 	help := []key.Binding{keys.choose, keys.remove}
//
// 	d.ShortHelpFunc = func() []key.Binding {
// 		return help
// 	}
//
// 	d.FullHelpFunc = func() [][]key.Binding {
// 		return [][]key.Binding{help}
// 	}
//
// 	return d
// }
//
// type delegateKeyMap struct {
// 	choose key.Binding
// 	remove key.Binding
// }
//
// // Additional short help entries. This satisfies the help.KeyMap interface and
// // is entirely optional.
// func (d delegateKeyMap) ShortHelp() []key.Binding {
// 	return []key.Binding{
// 		d.choose,
// 		d.remove,
// 	}
// }
//
// // Additional full help entries. This satisfies the help.KeyMap interface and
// // is entirely optional.
// func (d delegateKeyMap) FullHelp() [][]key.Binding {
// 	return [][]key.Binding{
// 		{
// 			d.choose,
// 			d.remove,
// 		},
// 	}
// }
//
// func newDelegateKeyMap() *delegateKeyMap {
// 	return &delegateKeyMap{
// 		choose: key.NewBinding(
// 			key.WithKeys("enter"),
// 			key.WithHelp("enter", "choose"),
// 		),
// 		remove: key.NewBinding(
// 			key.WithKeys("x", "backspace"),
// 			key.WithHelp("x", "delete"),
// 		),
// 	}
// }
//
// func handleKeyMsg(m model, msg tea.KeyMsg) (tea.Model, tea.Cmd) {
//
// 	switch {
// 	case key.Matches(msg, m.keys.toggleSpinner):
// 		cmd := m.list.ToggleSpinner()
// 		return m, cmd
//
// 	case key.Matches(msg, m.keys.toggleTitleBar):
// 		v := !m.list.ShowTitle()
// 		m.list.SetShowTitle(v)
// 		m.list.SetShowFilter(v)
// 		m.list.SetFilteringEnabled(v)
// 		return m, nil
//
// 	case key.Matches(msg, m.keys.toggleStatusBar):
// 		m.list.SetShowStatusBar(!m.list.ShowStatusBar())
// 		return m, nil
//
// 	case key.Matches(msg, m.keys.togglePagination):
// 		m.list.SetShowPagination(!m.list.ShowPagination())
// 		return m, nil
//
// 	case key.Matches(msg, m.keys.toggleHelpMenu):
// 		m.list.SetShowHelp(!m.list.ShowHelp())
// 		return m, nil
//
// 	case key.Matches(msg, m.keys.insertItem):
// 		m.delegateKeys.remove.SetEnabled(true)
// 		// newItem := m.itemGenerator.next()
// 		newItem := listItem{title: "New Item from lazytask", desc: "This is a new item."}
//
// 		// TODO:
// 		// if _, err = entities.LazyTask.AddTask(newItem); err != nil {
// 		insCmd := m.list.InsertItem(0, newItem)
// 		statusCmd := m.list.NewStatusMessage(statusMessageStyle("Added " + newItem.Title()))
// 		return m, tea.Batch(insCmd, statusCmd)
// 		// }
// 	}
//
// 	// switch msg.String() {
// 	// case "q", "esc", "ctrl+c":
// 	// 	return m, tea.Quit
// 	// }
//
// 	return m, nil
// }
//
// func createKeyBindings(listKeys *listKeyMap) []key.Binding {
// 	return []key.Binding{
// 		listKeys.toggleSpinner,
// 		listKeys.insertItem,
// 		listKeys.toggleTitleBar,
// 		listKeys.toggleStatusBar,
// 		listKeys.togglePagination,
// 		listKeys.toggleHelpMenu,
// 	}
// }
