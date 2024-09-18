package tasks

import (
	"encoding/json"
	"fmt"
	do "lazytask/domain"
	re "lazytask/task-controllers/reminders"
	"log"
	"os/exec"
	"slices"
)

type Reminders struct{}

// Lists

func (rem Reminders) GetLists() []do.List {
	remLists := execCommand[[]re.ReminderList]([]string{"show-lists"})
	if remLists != nil {
		var lists []do.List
		for _, rl := range remLists {
			lists = slices.Insert(lists, len(lists), re.ReminderListToList(rl))
		}

		return lists
	}

	return []do.List{}
}
func (rem Reminders) GetListById(id string) do.List {
	remList := execCommand[re.ReminderList]([]string{"show", id})
	if remList != nil {
		return re.ReminderListToList(remList)
	}

	return nil
}

// Tasks

func GetTaskById(taskId string) do.Task {

	return execCommand[do.Task]([]string{"show", taskId}) // TODO: This is broken

}
func GetTasksByList(listId string) []do.Task {
	return execCommand[[]do.Task]([]string{"show", "" + listId + ""})
	// TODO: reminders-cli can't handle lists with multiple workds yet
	// return execCommand[[]do.Task]([]string{"show", "'" + listId + "'"})

}

func AddTask(task do.Task) error {
	execCommand[do.Task]([]string{"add", "task", task.Title})
	return nil
}
func MoveTaskToList(taskId string, targetListId string) error {

	return nil
}

func CompleteTask(taskId string) error {

	return nil
}
func UncompleteTask(taskId string) error {

	return nil
}

// TODO: this needs to be absolute?
// What if we move the executable to /usr/bin/local?
// use os.Getwd()
const EXECUTABLE_PATH = "adapters/reminders-cli/reminders"

func execCommand[T any](commandArgs []string) (T, error) {
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
		return nil
	}

	return result
}
