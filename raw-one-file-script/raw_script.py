#!/usr/bin/env python3
"""
Equivalent Python script of raw_script.sh
Creates a consolidated dump of all text files in a Git repository into output.txt
Respects .gitignore, archives previous output.txt, skips binary files by extension, and provides progress/stats.
Optimized with parallel chunk processing using multiple processes, chunked reading (1000 files per chunk) for massive projects,
and large output buffering (1MB) for high performance.
Suitable for projects with millions of lines of code.
"""

import os
import sys
import shutil
import subprocess
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Known binary file extensions to skip
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp',
    '.exe', '.bin', '.dll', '.so', '.dylib', '.zip', '.tar', '.gz', '.rar', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
    '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
    '.ttf', '.otf', '.woff', '.woff2','.eot'
}

def is_binary_file(filename):
    """Check if file is likely binary based on extension."""
    return any(filename.lower().endswith(ext) for ext in BINARY_EXTENSIONS)

def read_file(file_path):
    """Read the content of a file, return empty string on error."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except IOError:
        return ""

def process_chunk(chunk_files, chunk_paths):
    """Process a chunk: read files in parallel, return combined text and stats."""
    with ThreadPoolExecutor(max_workers=16) as executor:  # Smaller pool per process
        contents = list(executor.map(read_file, chunk_paths))
    
    text_parts = []
    file_count = 0
    char_count = 0
    line_count = 0
    for file, content in zip(chunk_files, contents):
        text_parts.append(f"##### {file} #####\n{content}\n\n")
        file_count += 1
        char_count += len(content)
        line_count += content.count('\n')
    
    combined_text = ''.join(text_parts)
    return combined_text, file_count, char_count, line_count

def main():
    script_start = time.time()
    print(f"[INFO] Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)

    # Usage: python raw_script.py [repo_directory]
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    # Check if repo directory exists
    if not os.path.isdir(repo_dir):
        print(f"[ERROR] Directory '{repo_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Get absolute path to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create archive folder if needed
    archive_dir = os.path.join(script_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    # Timestamp for archiving
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # If output.txt exists, archive it
    output_file = os.path.join(script_dir, 'output.txt')
    if os.path.isfile(output_file):
        archived_file = os.path.join(archive_dir, f'output_{timestamp}.txt')
        shutil.move(output_file, archived_file)

    print(f"[INFO] Creating repo dump: {output_file}")

    # Gather file list (respecting .gitignore, skip archive)
    print("[INFO] Gathering file list from Git...", file=sys.stderr)
    list_start = time.time()
    try:
        result = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        all_files = [line for line in result.stdout.splitlines() if not line.startswith('archive/')]
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to run git ls-files: {e}", file=sys.stderr)
        sys.exit(1)
    list_end = time.time()
    print(f"[INFO] File listing completed in {list_end - list_start:.2f} seconds. Found {len(all_files)} total files.", file=sys.stderr)

    # Filter out known binary files by extension
    print("[INFO] Filtering binary files...", file=sys.stderr)
    filter_start = time.time()
    files = [f for f in all_files if not is_binary_file(f)]
    skipped = len(all_files) - len(files)
    filter_end = time.time()
    print(f"[INFO] Filtering completed in {filter_end - filter_start:.2f} seconds.", file=sys.stderr)

    total = len(files)

    print(f"[INFO] Processing {total} files...")
    if skipped > 0:
        print(f"[INFO] Skipped {skipped} binary files by extension", file=sys.stderr)
    print()

    # Prepare progress checkpoints (10%, 20%, ...)
    checkpoints = list(range(10, 101, 10))
    next_checkpoint = 10

    count = 0
    total_lines = 0
    total_chars = 0

    file_paths = [os.path.join(repo_dir, file) for file in files]
    chunk_size = 1000  # Process in chunks to limit memory usage for massive projects
    total_chunks = (len(files) + chunk_size - 1) // chunk_size  # Ceiling division

    print(f"[INFO] Starting parallel chunk processing with {min(total_chunks, 8)} processes...", file=sys.stderr)
    read_start = time.time()

    # Prepare chunk data
    chunks_data = []
    for i in range(0, len(files), chunk_size):
        chunk_files = files[i:i + chunk_size]
        chunk_paths = file_paths[i:i + chunk_size]
        chunks_data.append((chunk_files, chunk_paths))

    # Process chunks in parallel using processes
    max_workers = min(total_chunks, 8)  # Limit to 8 processes
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_chunk, cf, cp) for cf, cp in chunks_data]
        chunk_results = [future.result() for future in futures]

    read_end = time.time()
    print(f"[INFO] Chunk processing completed in {read_end - read_start:.2f} seconds.", file=sys.stderr)

    # Now write sequentially to output file
    print(f"[INFO] Writing combined output...", file=sys.stderr)
    write_start = time.time()
    with open(output_file, 'w', encoding='utf-8', buffering=1048576) as outfile:  # 1MB buffering for faster writes
        for combined_text, file_count, char_count, line_count in chunk_results:
            outfile.write(combined_text)
            count += file_count
            total_chars += char_count
            total_lines += line_count

            # Log progress only at checkpoints
            percent = count * 100 // total
            if percent >= next_checkpoint:
                print(f"[INFO] {next_checkpoint}% completed ({count}/{total} files)", file=sys.stderr)
                next_checkpoint += 10

    write_end = time.time()
    print(f"[INFO] Output writing completed in {write_end - write_start:.2f} seconds.", file=sys.stderr)

    # Stats
    file_size = os.path.getsize(output_file)
    size_str = f"{file_size // 1024}K" if file_size >= 1024 else f"{file_size}B"
    tokens = total_chars // 4
    script_end = time.time()
    total_duration = script_end - script_start

    print()
    print(f"[DONE] Repo dump created: {output_file}")
    print(f"[INFO] Total files processed: {total}")
    print(f"[INFO] Total lines in dump: {total_lines}")
    print(f"[INFO] Total size of dump: {size_str}")
    print(f"[INFO] Approx token count (chars/4): {tokens}")
    print(f"[INFO] Phase times: Listing {list_end - list_start:.2f}s, Filtering {filter_end - filter_start:.2f}s, Processing {read_end - read_start:.2f}s, Writing {write_end - write_start:.2f}s")
    print(f"[INFO] Total time taken: {total_duration:.2f} seconds")
    print(f"[INFO] Script finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
