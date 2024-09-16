package main

import (
	"lazytask/domain"
	tasks "lazytask/task-controllers"
	"lazytask/ui"
)

func main() {
	tasksImpl := tasks.Reminders{}
	ui := ui.Cli{}
	lazytask := domain.NewLazyTask(tasksImpl, ui)

	lazytask.Init()
}

// TODO:
// list reminders and archive
// come up with features
// performance & caching
