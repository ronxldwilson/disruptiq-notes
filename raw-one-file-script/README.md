# Raw One-File Script

This repository contains a Bash script (`raw_script.sh`) that creates a consolidated dump of all files in a Git repository into a single text file. It respects `.gitignore` rules and excludes the `archive` directory itself.

## What It Does

- Scans a Git repository for all tracked and untracked files (respecting `.gitignore`)
- Automatically skips binary files by extension (e.g., .png, .jpg, .exe) to ensure clean text output suitable for LLMs
- Concatenates the contents of text files into a single output file, separated by file headers
- Provides progress updates during processing
- Outputs statistics (file count, lines, size, approximate token count, execution time)
- Saves the dump to `output.txt` next to the script
- If `output.txt` already exists, archives the old one to `archive/output_YYYYMMDD_HHMMSS.txt`

## Prerequisites

- **Git**: Must be installed and the target directory must be a Git repository

### For Bash Version (raw_script.sh)

- **Bash shell**: Required to run the script
- **Unix-like tools**: Commands like `cat`, `wc`, `du`, `grep` must be available

### For Python Version (raw_script.py)

- **Python 3**: Required to run the script
- **No additional Unix tools needed**: All handled by Python libraries

### On Windows

Since you're on Windows, you'll need a compatible environment:
- **For Bash**: Git for Windows (includes Git Bash), WSL, or Cygwin
- **For Python**: Python 3 installed (can run directly in Command Prompt/PowerShell)

## How to Run

### Bash Version

1. Open your terminal (Git Bash, WSL, Command Prompt with Bash in PATH, etc.)
2. Navigate to this directory: `cd f:\disruptiq-notes\raw-one-file-script`
3. Run the script: `bash ./raw_script.sh [repo_directory]`
   - `[repo_directory]` is optional. If omitted, uses the current directory.
   - Example: `bash ./raw_script.sh ./cal.com`

### Python Version

1. Ensure Python 3 is installed and in your PATH
2. Open your terminal (Command Prompt, PowerShell, Git Bash, etc.)
3. Navigate to this directory: `cd f:\disruptiq-notes\raw-one-file-script`
4. Run the script: `python raw_script.py [repo_directory]`
   - `[repo_directory]` is optional. If omitted, uses the current directory.
   - Example: `python raw_script.py ./next-test-app`

## Examples

### Bash Examples

```bash
# Run on the current directory
bash ./raw_script.sh

# Run on a specific subdirectory (must be a Git repo)
bash ./raw_script.sh ./next-test-app

# Run on an absolute path
bash ./raw_script.sh /path/to/your/repo
```

### Python Examples

```bash
# Run on the current directory
python raw_script.py

# Run on a specific subdirectory (must be a Git repo)
python raw_script.py ./cal.com

# Run on an absolute path
python raw_script.py /path/to/your/repo
```

## Output

Both Bash and Python versions produce identical results:
- Create an `archive/` directory if it doesn't exist and archiving is needed
- Generate `output.txt` (archiving any existing file to `archive/output_YYYYMMDD_HHMMSS.txt`)
- Display progress (10%, 20%, etc.) and final stats

Example output:
```
[INFO] Creating repo dump: output.txt
[INFO] Processing 42 files...
[INFO] Skipped 5 binary/non-text files
[INFO] 10% completed (4/37 files)
...
[DONE] Repo dump created: output.txt
[INFO] Total files processed: 37
[INFO] Total lines in dump: 1234
[INFO] Total size of dump: 56K
[INFO] Approx token count (chars/4): 7890
[INFO] Total time taken: 2.34 seconds
```

## Notes

- The script skips the `archive/` directory itself to avoid infinite recursion
- If `output.txt` exists, it's automatically archived before creating the new one (archived files are stored in `archive/` with timestamps for easy retrieval)
- Large repositories may take time to process; progress is logged to stderr
- The approximate token count assumes 4 characters per token (common for LLM processing)
- Ensure you have write permissions in the script's directory

## Troubleshooting

### For Bash Version
- **Permission denied**: Run with `bash ./raw_script.sh` instead of `./raw_script.sh` on Windows
- **Command not found (e.g., wc, du)**: Ensure you're using a Bash environment with Unix tools

### For Python Version
- **Python not found**: Install Python 3 and ensure it's in your PATH
- **Module errors**: The script uses only standard library modules

### General
- **Directory not found**: Ensure the repo directory exists and is a Git repository
- **Git not found**: Install Git and ensure it's in your PATH
