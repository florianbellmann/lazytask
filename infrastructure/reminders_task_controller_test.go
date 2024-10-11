package infrastructure

import (
	"encoding/json"
	"log"
	"testing"
)

// Test parsing of ReminderLists to domain.Lists
func TestListParsing(t *testing.T) {
	mockResponse := `[
	"FirstList",
	"Second list",
	"Third list"
	]` // Even with trailing comma, it should parse correctly

	var reminderLists []ReminderList
	err := json.Unmarshal([]byte(mockResponse), &reminderLists)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %s", err)
	}

	// log.Printf("Reminder lists: %v", reminderLists)

	lists := parseLists(reminderLists)
	if lists[0].Id != "FirstList" ||
		lists[1].Id != "Second list" ||
		lists[2].Id != "Third list" ||
		len(lists) != 3 {
		t.Errorf("Failed to parse lists")
	}

}

func TestParseEmptyList(t *testing.T) {
	mockResponse := "[]"

	var reminderLists []ReminderList
	json.Unmarshal([]byte(mockResponse), &reminderLists)

	lists := parseLists(reminderLists)
	if len(lists) != 0 {
		t.Errorf("Failed to parse empty list")
	}
}

func TestGetListIndex(t *testing.T) {
	taskId := "810AE4D8-82FC-45BF-A0D2-C25E6205B178"
	listName, listIndex, err := getListAndIndexForCompletion(taskId)
	if err != nil {
		log.Fatalf("Failed to get index and list for: %s", taskId)
	}

	if listName != "develop" || listIndex != 2 {
		t.Errorf("Failed to get the correct listName or listIndex")
	}
}
