package domain

type LazyTask struct {
	tasks Tasks
	ui    Ui
}

func NewLazyTask(tasks Tasks, ui Ui) *LazyTask {
	return &LazyTask{tasks: tasks, ui: ui}
}

func (lt *LazyTask) Start() {
	lt.ui.ShowTasks(lt.tasks.GetTasks())
}
