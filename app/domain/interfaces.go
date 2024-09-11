package domain

type Tasks interface {
	GetTasks() []Task
}
type Ui interface {
	ShowTasks(tasks []Task)
}
