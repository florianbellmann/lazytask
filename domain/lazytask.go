package domain

type LazyTask struct {
	taskController TaskController
	ui             UI
	current_tasks  []Task
	lists          []List
}

func NewLazyTask(tasks TaskController, ui UI) *LazyTask {
	return &LazyTask{taskController: tasks, ui: ui}
}

func (lt *LazyTask) Init() {
	// lt.lists = lt.taskController.GetLists()
	// // lt.current_tasks = lt.taskController.GetTasksByList(lt.lists[0])
	// lt.current_tasks = lt.taskController.GetTasksByList("develop")

	lt.ui.Show(lt.current_tasks)
}
