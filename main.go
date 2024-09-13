package main

import (
	"lazytask/domain"
	"lazytask/task-controllers"
	"lazytask/ui"
)

func main() {
	tasksImpl := tasks.Reminders{}
	ui := ui.Cli{}
	lazytask := domain.NewLazyTask(tasksImpl, ui)

	lazytask.Init()
}
