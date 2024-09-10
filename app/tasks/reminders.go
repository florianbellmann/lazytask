import(
  "encoding/json"
	"log"
	"os/exec"
)

type Reminders struct{ }


func(t Reminders) GetTasks() []Task{

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
    tasks := []Task{}
    err = json.Unmarshal(output, &tasks)
    if err != nil {
      log.Fatalf("Failed to parse JSON: %s", err)
    }

    // Print the parsed struct
    fmt.Printf("Parsed struct: %+v\n", tasks)
    return tasks
}


go
Copy code
// RealService is a concrete implementation of Service
type RealService struct{}

// PerformTask implements the Service interface for RealService
func (s RealService) PerformTask() {
    fmt.Println("RealService: Performing the task")
}
