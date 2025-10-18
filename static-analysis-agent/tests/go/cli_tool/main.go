package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"time"
)

// Global variable - issue
var globalConfig = map[string]string{
	"debug": "true",
	"secret": "hardcoded-secret",
}

type Config struct {
	DatabaseURL string `json:"database_url"`
	APIKey      string `json:"api_key"`
	Debug       bool   `json:"debug"`
}

func main() {
	// Command line flags with issues
	inputFile := flag.String("input", "", "Input file")
	outputFile := flag.String("output", "output.txt", "Output file")
	command := flag.String("exec", "", "Command to execute")
	random := flag.Bool("random", false, "Generate random data")

	flag.Parse()

	if *random {
		generateRandomData()
	}

	if *inputFile != "" {
		processFile(*inputFile)
	}

	if *outputFile != "" {
		writeOutput(*outputFile, "sample data")
	}

	if *command != "" {
		executeCommand(*command)
	}
}

func processFile(filename string) {
	// Issue: path traversal vulnerability
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Printf("Error reading file: %v", err)
		return
	}

	fmt.Printf("File content: %s\n", string(data))
}

func writeOutput(filename, content string) {
	// Issue: no error handling for file operations
	ioutil.WriteFile(filename, []byte(content), 0644)
}

func executeCommand(cmd string) {
	// Security issue: command injection
	out, err := exec.Command("sh", "-c", cmd).CombinedOutput()
	if err != nil {
		log.Printf("Command error: %v", err)
	}
	fmt.Printf("Command output: %s\n", string(out))
}

func generateRandomData() {
	// Issue: using math/rand instead of crypto/rand
	rand.Seed(time.Now().UnixNano())

	for i := 0; i < 10; i++ {
		// Issue: predictable random numbers
		fmt.Printf("Random number: %d\n", rand.Intn(100))
	}
}

func loadConfig(filename string) (*Config, error) {
	// Issue: no file validation
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	var config Config
	json.Unmarshal(data, &config)
	return &config, nil
}

// Issue: unused function
func unusedHelper() string {
	return "This function is never used"
}

// Issue: poor naming
func badFunctionName() {
	fmt.Println("This function has a bad name")
}

// Issue: no error handling
func convertToInt(str string) int {
	result, _ := strconv.Atoi(str)
	return result
}

// Issue: global state modification
func incrementGlobal() {
	globalConfig["counter"] = "1"
}

func init() {
	// Issue: init function with side effects
	incrementGlobal()
}
