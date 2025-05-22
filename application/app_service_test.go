package application

import (
	"errors"
	"lazytask/entities"
	"reflect"
	"testing"
)

// In-memory implementation of Controller and Repository interfaces
// Repository extends Controller + SetList

type InMemController struct {
	tasksByList   map[string][]entities.Task
	lists         []entities.List
	completedTask map[string]bool
}

func NewInMemController(lists []entities.List) *InMemController {
	return &InMemController{
		tasksByList:   make(map[string][]entities.Task),
		lists:         lists,
		completedTask: make(map[string]bool),
	}
}

func (c *InMemController) GetLists() ([]entities.List, error) {
	return c.lists, nil
}

func (c *InMemController) GetListById(listId string) (entities.List, error) {
	for _, l := range c.lists {
		if l.Id == listId {
			return l, nil
		}
	}
	return entities.List{}, errors.New("list not found")
}

func (c *InMemController) GetTaskById(taskId string) (entities.Task, error) {
	for _, tasks := range c.tasksByList {
		for _, t := range tasks {
			if t.Id == taskId {
				return t, nil
			}
		}
	}
	return entities.Task{}, errors.New("task not found")
}

func (c *InMemController) GetTasksByList(listID string) ([]entities.Task, error) {
	return c.tasksByList[listID], nil
}

func (c *InMemController) AddTask(task entities.Task) error {
	c.tasksByList[task.ListId] = append(c.tasksByList[task.ListId], task)
	// if list not in known lists, track it
	found := false
	for _, l := range c.lists {
		if l.Id == task.ListId {
			found = true
			break
		}
	}
	if !found {
		c.lists = append(c.lists, entities.List{Id: task.ListId})
	}
	return nil
}

func (c *InMemController) CompleteTask(taskID string) error {
	c.completedTask[taskID] = true
	return nil
}

func (c *InMemController) UncompleteTask(taskID string) error {
	c.completedTask[taskID] = false
	return nil
}

func (c *InMemController) UpdateTask(task entities.Task) (entities.Task, error) {
	// find and replace in list
	tasks := c.tasksByList[task.ListId]
	for i, t := range tasks {
		if t.Id == task.Id {
			tasks[i] = task
			c.tasksByList[task.ListId] = tasks
			break
		}
	}
	return task, nil
}

func (c *InMemController) MoveTaskToList(taskID, targetListId string) error {
	// find task and remove from old list
	var moved entities.Task
	for listID, tasks := range c.tasksByList {
		for i, t := range tasks {
			if t.Id == taskID {
				moved = t
				moved.ListId = targetListId
				// remove from old
				c.tasksByList[listID] = append(tasks[:i], tasks[i+1:]...)
				// add to new
				c.tasksByList[targetListId] = append(c.tasksByList[targetListId], moved)
				// ensure list tracking
				if _, err := c.GetListById(targetListId); err != nil {
					c.lists = append(c.lists, entities.List{Id: targetListId})
				}
				return nil
			}
		}
	}
	return errors.New("task not found")
}

// In-memory implementation of Repository interface
// Repository embeds Controller

type InMemRepo struct {
	tasksByList   map[string][]entities.Task
	completedTask map[string]bool
}

func NewInMemRepo() *InMemRepo {
	return &InMemRepo{
		tasksByList:   make(map[string][]entities.Task),
		completedTask: make(map[string]bool),
	}
}

func (r *InMemRepo) GetLists() ([]entities.List, error) {
	var lists []entities.List
	for id := range r.tasksByList {
		lists = append(lists, entities.List{Id: id})
	}
	return lists, nil
}

func (r *InMemRepo) GetListById(listId string) (entities.List, error) {
	if _, ok := r.tasksByList[listId]; ok {
		return entities.List{Id: listId}, nil
	}
	return entities.List{}, errors.New("list not found")
}

func (r *InMemRepo) GetTaskById(taskId string) (entities.Task, error) {
	for _, tasks := range r.tasksByList {
		for _, t := range tasks {
			if t.Id == taskId {
				return t, nil
			}
		}
	}
	return entities.Task{}, errors.New("task not found")
}

func (r *InMemRepo) GetTasksByList(listID string) ([]entities.Task, error) {
	return r.tasksByList[listID], nil
}

func (r *InMemRepo) AddTask(task entities.Task) error {
	r.tasksByList[task.ListId] = append(r.tasksByList[task.ListId], task)
	return nil
}

func (r *InMemRepo) SetList(listID string, tasks []entities.Task) error {
	r.tasksByList[listID] = tasks
	return nil
}

func (r *InMemRepo) CompleteTask(taskID string) error {
	r.completedTask[taskID] = true
	return nil
}

func (r *InMemRepo) UncompleteTask(taskID string) error {
	r.completedTask[taskID] = false
	return nil
}

func (r *InMemRepo) UpdateTask(task entities.Task) (entities.Task, error) {
	// update in existing slice
	tasks := r.tasksByList[task.ListId]
	for i, t := range tasks {
		if t.Id == task.Id {
			tasks[i] = task
			r.tasksByList[task.ListId] = tasks
			break
		}
	}
	return task, nil
}

func (r *InMemRepo) MoveTaskToList(taskID, targetListId string) error {
	var moved entities.Task
	for listID, tasks := range r.tasksByList {
		for i, t := range tasks {
			if t.Id == taskID {
				moved = t
				moved.ListId = targetListId
				// remove from old
				r.tasksByList[listID] = append(tasks[:i], tasks[i+1:]...)
				// add to new
				r.tasksByList[targetListId] = append(r.tasksByList[targetListId], moved)
				return nil
			}
		}
	}
	return errors.New("task not found")
}

func TestFlow_GetListsSync(t *testing.T) {
	lists := []entities.List{{Id: "L1"}, {Id: "L2"}}
	ctrl := NewInMemController(lists)
	repo := NewInMemRepo()
	aps := NewAppService(repo, ctrl)

	out, err := aps.GetLists()
	if err != nil {
		t.Fatalf("GetLists failed: %v", err)
	}
	if !reflect.DeepEqual(out, lists) {
		t.Errorf("GetLists returned %v; want %v", out, lists)
	}

	// Repo should have an entry for each list (with nil slice)
	for _, l := range lists {
		saved := repo.tasksByList[l.Id]
		if saved != nil && len(saved) != 0 {
			t.Errorf("Repo SetList for %s = %v; want empty slice or nil", l.Id, saved)
		}
	}
}

func TestFlow_CompleteTaskSync(t *testing.T) {
	ctrl := NewInMemController(nil)
	repo := NewInMemRepo()
	aps := NewAppService(repo, ctrl)

	taskID := "T1"
	if err := aps.CompleteTask(taskID); err != nil {
		t.Fatalf("CompleteTask failed: %v", err)
	}

	// Controller should mark completed
	if !ctrl.completedTask[taskID] {
		t.Errorf("controller should have task %s marked complete", taskID)
	}

	// Repo should also mark completed
	if !repo.completedTask[taskID] {
		t.Errorf("repo should have task %s marked complete", taskID)
	}
}

func TestFlow_UpdateTaskSync(t *testing.T) {
	// Seed controller and repo
	task := entities.Task{Id: "T1", Title: "Old", ListId: "L1"}
	ctrl := NewInMemController([]entities.List{{Id: "L1"}})
	ctrl.AddTask(task)
	repo := NewInMemRepo()
	repo.AddTask(task)

	aps := NewAppService(repo, ctrl)

	updated := entities.Task{Id: "T1", Title: "New Name", ListId: "L1"}

	out, err := aps.UpdateTask(updated)
	if err != nil {
		t.Fatalf("UpdateTask failed: %v", err)
	}
	if !reflect.DeepEqual(out, updated) {
		t.Errorf("service returned %v; want %v", out, updated)
	}

	// Controller state
	ctrlTasks, _ := ctrl.GetTasksByList("L1")
	if !reflect.DeepEqual(ctrlTasks[0], updated) {
		t.Errorf("controller task = %v; want %v", ctrlTasks[0], updated)
	}

	// Repo state
	repoTasks := repo.tasksByList["L1"]
	if !reflect.DeepEqual(repoTasks[0], updated) {
		t.Errorf("repo task = %v; want %v", repoTasks[0], updated)
	}
}
