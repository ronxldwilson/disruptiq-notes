import os
import subprocess
import hashlib
import json
from pathlib import Path
from typing import List, Set, Dict, Optional

class Scanner:
    def __init__(self, config):
        self.config = config
        # Default ignore patterns for common directories/packages
        default_ignores = [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            ".env",
            "dist",
            "build",
            ".next",
            ".nuxt",
            "yarn.lock",
            ".yarn",
            "package-lock.json",
            ".DS_Store",
            "Thumbs.db"
        ]
        user_ignores = config.get("ignore_patterns", [])
        self.ignore_patterns = set(default_ignores + user_ignores)
        self.exclude_extensions = set(config.get("exclude_extensions", []))
        self.max_file_size_mb = config.get("max_file_size_mb", 10)
        self.prefer_git = config.get("prefer_git", True)  # New option to prefer git traversal

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on patterns."""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False

    def should_scan_file(self, file_path: Path) -> bool:
        """Check if a file should be scanned based on extension, size, and content."""
        # Check if extension is explicitly excluded
        if file_path.suffix.lower() in self.exclude_extensions:
            return False

        # Quick extension-based filtering for obviously non-code files
        non_code_extensions = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.ico', '.webp',
            # Videos
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
            # Audio
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',
            # Documents
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Archives
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            # Fonts
            '.ttf', '.otf', '.woff', '.woff2',
            # Other binary/non-code
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite', '.sqlite3'
        }
        if file_path.suffix.lower() in non_code_extensions:
            return False

        # Skip files in certain directories that are typically not source code
        path_str = str(file_path)
        non_code_dirs = ['/node_modules/', '/.git/', '/__pycache__/', '/.venv/', '/venv/', '/env/',
                        '/dist/', '/build/', '/.next/', '/.nuxt/', '/coverage/', '/.nyc_output/',
                        '/.pytest_cache/', '/.tox/', '/.eggs/', '/*.egg-info/']
        if any(non_code_dir in path_str for non_code_dir in non_code_dirs):
            return False

        # Check file size
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                return False
        except OSError:
            return False  # Skip if can't get size

        # Check if file is likely binary (contains null bytes in first 1024 bytes)
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
                if b'\x00' in sample:
                    return False  # Likely binary file
        except (OSError, IOError):
            return False  # Skip if can't read

        return True

    def scan_directory(self, root_path: str) -> List[Path]:
        """Recursively scan directory and return list of files to analyze."""
        root = Path(root_path).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid directory path: {root_path}")

        files_to_scan = []

        # Check if this is a git repository and use git ls-files for faster scanning
        # Check for .git in current directory or any parent directory
        git_root = None
        current = root
        while current.parent != current:  # Stop at filesystem root
            git_dir = current / '.git'
            if git_dir.exists() and git_dir.is_dir():
                git_root = current
                break
            current = current.parent

        use_git = self.prefer_git and git_root is not None

        if use_git:
            try:
                # Use git ls-files to get tracked files quickly, relative to git root
                # Include untracked files with --others, exclude ignored with --exclude-standard
                result = subprocess.run(
                    ['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                    cwd=str(git_root),
                    capture_output=True,
                    text=True,
                    timeout=60  # Increased timeout for large repos
                )
                if result.returncode == 0:
                    git_files = result.stdout.strip().split('\n')
                    print(f"Git repository detected - using git ls-files for fast traversal")
                    print(f"Git found {len(git_files)} tracked/untracked files")
                    for file_path in git_files:
                        if file_path:  # Skip empty lines
                            # Convert git-relative path to absolute path
                            full_path = git_root / file_path
                            # Only include files that are within our scan root
                            try:
                                full_path.relative_to(root)
                                # Skip files in ignored directories or with ignored patterns
                                if not self.should_ignore(full_path) and self.should_scan_file(full_path):
                                    files_to_scan.append(full_path)
                            except ValueError:
                                # File is outside our scan root, skip
                                pass
                    print(f"After filtering: {len(files_to_scan)} files to analyze")
                    return files_to_scan
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"Git command failed, falling back to directory scan: {e}")
                pass

        # Fallback: recursively scan directory
        print("Using directory traversal (no git repository detected or git failed)")
        for path in root.rglob('*'):
            if path.is_file() and not self.should_ignore(path) and self.should_scan_file(path):
                files_to_scan.append(path)

        return files_to_scan

    def scan_directory_incremental(self, root_path: str, cache_dir: str = ".obfuscation_cache") -> List[Path]:
        """Scan directory incrementally, only returning files that have changed since last run."""
        root = Path(root_path).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid directory path: {root_path}")

        cache_path = Path(cache_dir) / f"{hashlib.md5(str(root.absolute()).encode()).hexdigest()}.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if this is a git repository for potentially faster incremental scanning
        # Check for .git in current directory or any parent directory
        git_root = None
        current = root
        while current.parent != current:  # Stop at filesystem root
            git_dir = current / '.git'
            if git_dir.exists() and git_dir.is_dir():
                git_root = current
                break
            current = current.parent

        use_git_incremental = git_root is not None

        if use_git_incremental:
            try:
                # Use git status to find changed files quickly
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=str(git_root),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    changed_files = []
                    status_lines = result.stdout.strip().split('\n')
                    for line in status_lines:
                        if line.strip():
                            # Parse git status output (format: XY file_path)
                            status_code = line[:2]
                            file_path = line[2:].strip()
                            if file_path:
                                # Convert git-relative path to absolute path
                                full_path = git_root / file_path
                                # Only include files that are within our scan root
                                try:
                                    full_path.relative_to(root)
                                    # Include modified, added, renamed files
                                    if status_code[0] in 'MACR' or status_code[1] in 'MACR':
                                        if not self.should_ignore(full_path) and self.should_scan_file(full_path):
                                            changed_files.append(full_path)
                                except ValueError:
                                    # File is outside our scan root, skip
                                    pass
                    if changed_files:
                        print(f"Git incremental scan found {len(changed_files)} changed files")
                        return changed_files
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"Git incremental scan failed, falling back to full scan: {e}")
                pass

        # Load previous cache
        previous_cache = self._load_cache(cache_path)

        # Get all files that should be scanned
        all_files = self.scan_directory(root_path)

        # Filter to only changed files
        changed_files = []
        current_cache = {}

        for file_path in all_files:
            try:
                # Get file metadata
                stat = file_path.stat()
                file_key = str(file_path.relative_to(root))

                # Create hash of file content and metadata
                file_hash = self._get_file_hash(file_path, stat)

                current_cache[file_key] = {
                    'hash': file_hash,
                    'mtime': stat.st_mtime,
                    'size': stat.st_size
                }

                # Check if file has changed
                if file_key not in previous_cache or previous_cache[file_key] != current_cache[file_key]:
                    changed_files.append(file_path)

            except (OSError, IOError):
                # If we can't read the file, consider it changed
                changed_files.append(file_path)

        # Save current cache
        self._save_cache(cache_path, current_cache)

        if use_git_incremental:
            print(f"Incremental scan (fallback) found {len(changed_files)} changed files")
        else:
            print(f"Incremental scan found {len(changed_files)} changed files")

        return changed_files

    def _get_file_hash(self, file_path: Path, stat) -> str:
        """Get hash of file content and metadata."""
        try:
            # For small files, hash the content
            if stat.st_size < 1024 * 1024:  # 1MB
                with open(file_path, 'rb') as f:
                    content = f.read()
                    return hashlib.md5(content).hexdigest()
            else:
                # For large files, hash metadata only (size + mtime)
                metadata = f"{stat.st_size}_{stat.st_mtime}"
                return hashlib.md5(metadata.encode()).hexdigest()
        except (OSError, IOError):
            # Fallback to metadata hash
            metadata = f"{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(metadata.encode()).hexdigest()

    def _load_cache(self, cache_path: Path) -> Dict:
        """Load previous scan cache."""
        try:
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (OSError, IOError, json.JSONDecodeError):
            pass
        return {}

    def _save_cache(self, cache_path: Path, cache_data: Dict):
        """Save scan cache."""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except (OSError, IOError):
            # Silently fail if we can't save cache
            pass
