package tasks

import (
	"encoding/json"
	"fmt"
	"lazytask/domain"
	"log"
	"os/exec"
)

type Reminders struct{}

func (t Reminders) GetTasks() []domain.Task {

	// Run a shell command that outputs JSON (for demonstration, echo a JSON string)
	cmd := exec.Command("../adapters/reminders-cli/reminders", `show`, "develop", "--format", "json")

	// Capture the command output
	output, err := cmd.Output()
	if err != nil {
		log.Fatalf("Failed to run command: %s", err)
	}

	// Print the raw output (JSON string)
	fmt.Printf("Raw output: %s\n", string(output))

	// Parse the JSON into a Go struct
	tasks := []domain.Task{}
	err = json.Unmarshal(output, &tasks)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %s", err)
	}

	// Print the parsed struct
	fmt.Printf("Parsed struct: %+v\n", tasks)
	return tasks
}
