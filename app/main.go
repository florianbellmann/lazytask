package main

import (
	"lazytask/domain"
	"lazytask/tasks"
	"lazytask/ui"
)

func main() {
	tasksImpl := tasks.Reminders{}
	ui := ui.Cli{}
	lazytask := domain.NewLazyTask(tasksImpl, ui)

	lazytask.Start()
}
