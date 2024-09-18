package domain

import (
	"log"
	"os"
	"slices"
)

type LazyTask struct {
	taskController TaskController
	ui             UI

	current_tasks []Task
	lists         []List
}

func NewLazyTask(tasks TaskController, ui UI) *LazyTask {
	return &LazyTask{taskController: tasks, ui: ui}
}

func (lt *LazyTask) Init() {
	lt.lists = lt.taskController.GetLists()
	// lt.current_tasks = lt.taskController.GetTasksByList(lt.lists[0])
	lt.current_tasks = lt.taskController.GetTasksByList("develop")

	lt.ui.Show(lt.current_tasks)
}

func (lt *LazyTask) CompleteTask(taskExternalId string) {
	taskIndex := slices.IndexFunc(lt.current_tasks, func(t Task) bool { return t.ExternalID == taskExternalId })

	if taskIndex == -1 {
		log.Fatal("Can't find item index")
		os.Exit(1)
	}

	if err := lt.taskController.CompleteTask(lt.current_tasks[taskIndex]); err != nil {
		log.Fatal(err)
		os.Exit(1)
	} else {
		lt.current_tasks = slices.DeleteFunc(lt.current_tasks, func(t Task) bool { return t.ExternalID == taskExternalId })
	}

	// lt.ui.Update(lt.current_tasks)
}

func (lt *LazyTask) AddTask(taskExternalId string) {
	// taskIndex := slices.IndexFunc(lt.current_tasks, func(t Task) bool { return t.ExternalID == taskExternalId })
	//
	// if taskIndex == -1 {
	// 	log.Fatal("Can't find item index")
	// 	os.Exit(1)
	// }
	//
	// if err := lt.taskController.CompleteTask(lt.current_tasks[taskIndex]); err != nil {
	// 	log.Fatal(err)
	// 	os.Exit(1)
	// } else {
	// 	lt.current_tasks = slices.DeleteFunc(lt.current_tasks, func(t Task) bool { return t.ExternalID == taskExternalId })
	// }
	//
	// lt.ui.Update(lt.current_tasks)
}

is the LazyTask struct in this case a state object?
does DDD make sense here or do we just have pure functions?
state input, state output
passing it around

where is the state of truth ? how do I get the current state then?
func (lt *LazyTask) UpdateTask(task Task) {
	taskIndex := slices.IndexFunc(lt.current_tasks, func(t Task) bool { return t.ExternalID == task.ExternalID })

	if taskIndex == -1 {
		log.Fatal("Can't find item index")
		os.Exit(1)
	}

	lt.current_tasks[taskIndex] = task

	// lt.ui.Update(lt.current_tasks)
}
