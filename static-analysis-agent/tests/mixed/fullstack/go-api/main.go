package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"strconv"
)

type APIResponse struct {
	Data  interface{} `json:"data"`
	Error string      `json:"error,omitempty"`
}

func main() {
	http.HandleFunc("/api/data", dataHandler)
	http.HandleFunc("/api/calc", calcHandler)
	http.HandleFunc("/api/system", systemHandler)

	log.Println("Go API server starting on :8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}

func dataHandler(w http.ResponseWriter, r *http.Request) {
	// Issue: no CORS headers
	w.Header().Set("Content-Type", "application/json")

	id := r.URL.Query().Get("id")

	// Issue: no input validation
	data := map[string]interface{}{
		"id":   id,
		"name": fmt.Sprintf("Item %s", id),
	}

	json.NewEncoder(w).Encode(APIResponse{Data: data})
}

func calcHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	aStr := r.URL.Query().Get("a")
	bStr := r.URL.Query().Get("b")

	// Issue: no error handling for atoi
	a, _ := strconv.Atoi(aStr)
	b, _ := strconv.Atoi(bStr)

	// Issue: division by zero not handled
	result := a / b

	json.NewEncoder(w).Encode(APIResponse{Data: map[string]int{"result": result}})
}

func systemHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	cmd := r.URL.Query().Get("cmd")

	// Security issue: command injection
	out, err := exec.Command("sh", "-c", cmd).Output()

	response := APIResponse{}
	if err != nil {
		response.Error = err.Error()
	} else {
		response.Data = string(out)
	}

	json.NewEncoder(w).Encode(response)
}

// Issue: unused function
func unusedGoFunction() string {
	return "Never called"
}
