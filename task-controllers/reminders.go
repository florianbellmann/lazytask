package tasks

import (
	"encoding/json"
	"fmt"
	do "lazytask/domain"
	"log"
	"os/exec"
)

type Reminders struct{}

// Lists
func (rem Reminders) GetLists() []do.List {
	return execCommand[[]do.List]([]string{"show-lists"})
}
func (rem Reminders) GetListById(id string) do.List {
	return execCommand[do.List]([]string{"show", id})
}

// Tasks

// func (rem Reminders) GetTaskById(listId, string, id string) do.Task {
func (rem Reminders) GetTaskById(id string) do.Task {
	// listTasks := rem.GetTasksByList(listId)
	// return listTasks.CompleteTaskn
	return execCommand[do.Task]([]string{"show", id}) // TODO: This is broken
}
func (rem Reminders) GetTasksByList(listId string) []do.Task {
	return execCommand[[]do.Task]([]string{"show", "" + listId + ""})
	// TODO: reminders-cli can't handle lists with multiple workds yet
	// return execCommand[[]do.Task]([]string{"show", "'" + listId + "'"})
}

func (rem Reminders) AddTask(task do.Task) {
	execCommand[do.Task]([]string{"add", "task", task.Title})
}
func (rem Reminders) MoveTaskToList(task do.Task, list do.List) {
	// TBD set comand
}

func (rem Reminders) CompleteTask(task do.Task) {
	// TBD set comand
}
func (rem Reminders) UncompleteTask(task do.Task) {
	// TBD set comand
}

// Private functions
// cwd, err := os.Getwd()
//
//	if err != nil {
//	  fmt.Println(err)
//	} else {
//
//	  fmt.Println("Current working directory:", cwd)
//	}
//
// TODO: this needs to be absolute?
// What if we move the executable to /usr/bin/local?
const EXECUTABLE_PATH = "adapters/reminders-cli/reminders"

func execCommand[T any](commandArgs []string) T {
	commandArgs = append(commandArgs, "--format", "json")

	// Run the command
	cmd := exec.Command(EXECUTABLE_PATH, commandArgs...)
	output, err := cmd.Output()

	if err != nil {
		log.Printf("Running command: %s", cmd)
		fmt.Printf("Raw output: %s\n", string(output))
		log.Fatalf("Failed to run command: %s", err)
	}

	// Parse the JSON into a Go struct
	var result T
	err = json.Unmarshal(output, &result)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %s", err)
	}

	// Print the parsed struct
	// fmt.Printf("Parsed struct: %+v\n", tasks)
	return result
}
