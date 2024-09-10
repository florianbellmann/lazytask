package main

import (
	"fmt"
	"log"
	"time"
)

// Interfaces
type Tasks interface {
	GetTasks() []Task
}
type Ui interface {
	ShowTasks(tasks []Task)
}

// DI:
// Controller depends on Service, and this dependency is injected via constructor
type Controller struct {
	service Service
}

// NewController is the constructor that accepts a Service as a dependency
func NewController(service Service) *Controller {
	return &Controller{service: service}
}

// HandleRequest uses the injected service to perform some operation
func (c *Controller) HandleRequest() {
	c.service.PerformTask()
}

type LazyTask struct {
	task Task
}

func NewLazyTask(task Task, ui Ui) *LazyTask {

}

func main() {
	tasks := Reminders{}
	ui := Cli{}
	lazytask := NewLazyTask(tasks, ui)

	lazytask.Start()
}
