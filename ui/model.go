package ui

import (
	"github.com/charmbracelet/bubbles/list"
	"lazytask/application"
	"lazytask/domain"
)

type taskItem struct {
	task domain.Task
}

func (t taskItem) Title() string {
	return t.task.Title
}

func (t taskItem) Description() string {
	return t.task.Description
}

func (t taskItem) FilterValue() string {
	return t.task.Title
}

type Model struct {
	lists        []domain.List
	tasks        []domain.Task
	selectedList int
	taskService  *application.TaskService
	err          error
	listModel    list.Model // Bubble Tea's Fancy List
}

func NewModel(taskService *application.TaskService) Model {
	// Initialize the Fancy List with a title and an empty set of tasks
	fancyList := list.New([]list.Item{}, list.NewDefaultDelegate(), 0, 0)
	fancyList.Title = "Tasks"

	return Model{
		lists:        []domain.List{},
		tasks:        []domain.Task{},
		selectedList: 0,
		taskService:  taskService,
		listModel:    fancyList,
	}
}

// Load tasks into the Fancy List
func (m *Model) LoadTasks(tasks []domain.Task) {
	items := []list.Item{}
	for _, task := range tasks {
		items = append(items, taskItem{task: task})
	}
	m.listModel.SetItems(items)
}
