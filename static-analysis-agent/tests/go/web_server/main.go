package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strconv"
)

// Global variables - issue
var (
	globalCounter = 0
	db            *sql.DB
)

type User struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

func main() {
	// Issue: no error handling
	db = initDB()

	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/api/users/", userHandler)
	http.HandleFunc("/api/exec", execHandler)
	http.HandleFunc("/api/upload", uploadHandler)

	// Issue: hardcoded port
	log.Println("Server starting on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func initDB() *sql.DB {
	// Issue: hardcoded credentials
	db, _ := sql.Open("mysql", "user:password@tcp(localhost:3306)/mydb")
	return db
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	// Issue: XSS vulnerability - direct HTML output
	name := r.URL.Query().Get("name")
	if name == "" {
		name = "World"
	}

	// Issue: HTML template without proper escaping
	html := fmt.Sprintf("<h1>Hello %s!</h1>", name)
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(html))
}

func userHandler(w http.ResponseWriter, r *http.Request) {
	// Issue: SQL injection
	id := r.URL.Query().Get("id")

	// Issue: direct string formatting in SQL
	query := fmt.Sprintf("SELECT id, name, email FROM users WHERE id = %s", id)

	rows, err := db.Query(query)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var user User
		rows.Scan(&user.ID, &user.Name, &user.Email)
		users = append(users, user)
	}

	json.NewEncoder(w).Encode(users)
}

func execHandler(w http.ResponseWriter, r *http.Request) {
	// Security issue: command injection
	cmd := r.URL.Query().Get("cmd")

	// Issue: executing user input
	out, err := exec.Command("sh", "-c", cmd).Output()
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	w.Write(out)
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	// Issue: no file size limits
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, err.Error(), 400)
		return
	}
	defer file.Close()

	// Issue: no path validation
	filename := header.Filename
	out, err := os.Create(filename)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer out.Close()

	// Issue: no error handling for copy
	file.Seek(0, 0)
	out.ReadFrom(file)

	w.Write([]byte("File uploaded"))
}

// Issue: unused function
func unusedFunction() string {
	return "This function is never called"
}

// Issue: poor error handling
func parseID(idStr string) int {
	// Issue: no error checking
	id, _ := strconv.Atoi(idStr)
	return id
}
