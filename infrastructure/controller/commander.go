package infrastructure

//TODO: hardening https://chatgpt.com/c/6818a8ec-47e4-800c-8c06-33b4672f7467

import (
	"fmt"
	"log"
	"os/exec"
)

type Commander interface {
	// Exec returns raw combined stdout+stderr.
	Exec(args []string) ([]byte, error)
	ExecWithoutOutput(args []string) error
}

// Real implementation that shells out to your reminders CLI.
type CliCommander struct{}

// Runs an external command and discards the output
func (c CliCommander) ExecWithoutOutput(commandArgs []string) error {
	_, err := c.rawExec(commandArgs)
	if err != nil {
		return err
	}

	return nil
}

// execCommand runs an external command and parses the JSON result
func (c CliCommander) Exec(commandArgs []string) ([]byte, error) {
	// Add JSON format flag for response
	commandArgs = append(commandArgs, "--format", "json")

	return c.rawExec(commandArgs)
}

func (c CliCommander) rawExec(commandArgs []string) ([]byte, error) {
	execPath, execPathErr := getExecutablePath()
	if execPathErr != nil {
		return nil, execPathErr
	}

	// Run the command
	log.Printf("Executing raw command: %s %v", execPath, commandArgs)
	cmd := exec.Command(execPath, commandArgs...)

	// Capture both stdout and stderr
	output, err := cmd.CombinedOutput()

	if err != nil {
		return nil, fmt.Errorf("Command failed: %s - Error: %v", string(output), err)
	}

	return output, nil
}
