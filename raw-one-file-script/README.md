# Raw One-File Script

This repository contains scripts to create a consolidated dump of all text files in a Git repository into a single `output.txt` file. The primary version is a highly optimized Python script (`raw_script.py`), with a Bash alternative (`raw_script.sh`). Both respect `.gitignore` rules, skip binary files, and archive previous outputs.

## What It Does (Python Version)

The Python script (`raw_script.py`) is optimized for massive codebases (e.g., 30M+ lines of code) and includes advanced features:

- **Git Integration**: Uses `git ls-files` to scan tracked/untracked files, respecting `.gitignore` and excluding the `archive/` directory.
- **Binary File Filtering**: Skips known binary extensions (e.g., .png, .jpg, .exe, .pdf) to ensure clean text output.
- **Parallel Processing**: Processes files in chunks (1000 files each) using multiple processes for parallel execution, with intra-chunk threading for file reading.
- **Memory Management**: Chunked processing limits memory usage for large repos.
- **Progress & Logging**: Detailed phase timings, per-chunk updates, and progress checkpoints (10%, 20%, etc.).
- **Output Handling**: Concatenates text files with separators (`##### filename #####`), archives old `output.txt` to `archive/`, and provides stats (files, lines, size, tokens, time).
- **Performance**: Uses large buffering, process pools, and optimizations for I/O-bound tasks, aiming for sub-minute processing on massive projects.

## How the Python Script Works

The script follows a phased approach for efficiency:

1. **Initialization & Archiving**:
   - Checks the repo directory, gets script paths.
   - Archives existing `output.txt` to `archive/output_YYYYMMDD_HHMMSS.txt` if present.

2. **File Discovery**:
   - Runs `git ls-files --cached --others --exclude-standard` to list all files (tracked/untracked, ignoring `.gitignore`).
   - Filters out binary files by checking extensions against a predefined set.
   - Excludes `archive/` to prevent recursion.

3. **Parallel Chunk Processing**:
   - Divides files into chunks of 1000.
   - Uses `ProcessPoolExecutor` (up to 8 processes) to process chunks in parallel.
   - Each process: Reads files in the chunk using `ThreadPoolExecutor` (16 threads), combines into text blocks, returns stats.

4. **Output Writing**:
   - Main thread writes chunk results sequentially to `output.txt` with 1MB buffering for speed.
   - Logs progress at 10% intervals.

5. **Statistics & Cleanup**:
   - Computes file size, lines, chars, tokens (chars/4 estimate).
   - Prints phase times (listing, filtering, processing, writing) and total duration.

**Key Optimizations**:
- **Parallelism**: Multi-process for chunks, multi-threaded for I/O within chunks.
- **Memory**: Chunking prevents loading all data at once.
- **I/O**: Large buffers, UTF-8 encoding with error ignoring.
- **Error Handling**: Skips unreadable files gracefully.

For massive repos, this enables processing 30M LOC in ~1-2 minutes on modern hardware.

## Prerequisites

- **Git**: Must be installed and the target directory must be a Git repository

### For Bash Version (raw_script.sh)

- **Bash shell**: Required to run the script
- **Unix-like tools**: Commands like `cat`, `wc`, `du`, `grep` must be available

### For Python Version (raw_script.py)

- **Python 3.6+**: Required to run the script (uses concurrent.futures for parallelism)
- **No additional Unix tools needed**: All handled by Python standard libraries

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

Example output for a small repo:
```
[INFO] Script started at: 2025-10-21 00:50:45
[INFO] Gathering file list from Git...
[INFO] File listing completed in 0.08 seconds. Found 21 total files.
[INFO] Filtering binary files...
[INFO] Filtering completed in 0.00 seconds.
[INFO] Skipped 6 binary files by extension
[INFO] Starting parallel chunk processing with 1 processes...
[INFO] Chunk processing completed in 0.37 seconds.
[INFO] Writing combined output...
[INFO] 10% completed (2/16 files)
...
[DONE] Repo dump created: output.txt
[INFO] Total files processed: 16
[INFO] Total lines in dump: 6414
[INFO] Total size of dump: 225K
[INFO] Approx token count (chars/4): 56001
[INFO] Phase times: Listing 0.08s, Filtering 0.00s, Processing 0.37s, Writing 0.00s
[INFO] Total time taken: 0.46 seconds
[INFO] Script finished at: 2025-10-21 00:50:45
```

For massive repos, you'll see more processes and faster chunk processing.

## Notes

- The script skips the `archive/` directory itself to avoid infinite recursion
- If `output.txt` exists, it's automatically archived before creating the new one (archived files are stored in `archive/` with timestamps for easy retrieval)
- Large repositories may take time to process; progress is logged to stderr with detailed phase timings
- The approximate token count assumes 4 characters per token (common for LLM processing)
- Ensure you have write permissions in the script's directory
- For massive repos (30M+ LOC), the Python script's parallel chunk processing can reduce time to under 2 minutes on multi-core systems

## Troubleshooting

### For Bash Version
- **Permission denied**: Run with `bash ./raw_script.sh` instead of `./raw_script.sh` on Windows
- **Command not found (e.g., wc, du)**: Ensure you're using a Bash environment with Unix tools

### For Python Version
- **Python not found**: Install Python 3.6+ and ensure it's in your PATH
- **Module errors**: The script uses standard library modules (concurrent.futures for parallelism)
- **Performance issues**: For massive repos, ensure multi-core CPU; adjust chunk_size in code if memory is limited

### General
- **Directory not found**: Ensure the repo directory exists and is a Git repository
- **Git not found**: Install Git and ensure it's in your PATH
