import os
import subprocess
from pathlib import Path
from typing import List, Set

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
            "package-lock.json",
            ".DS_Store",
            "Thumbs.db"
        ]
        user_ignores = config.get("ignore_patterns", [])
        self.ignore_patterns = set(default_ignores + user_ignores)
        self.exclude_extensions = set(config.get("exclude_extensions", []))
        self.max_file_size_mb = config.get("max_file_size_mb", 10)

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
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid directory path: {root_path}")

        files_to_scan = []

        # Check if this is a git repository and use git ls-files for faster scanning
        git_dir = root / '.git'
        if git_dir.exists() and git_dir.is_dir():
            try:
                # Use git ls-files to get tracked files quickly
                result = subprocess.run(
                    ['git', 'ls-files'],
                    cwd=root_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    git_files = result.stdout.strip().split('\n')
                    for file_path in git_files:
                        if file_path:  # Skip empty lines
                            full_path = root / file_path
                            # Skip files in ignored directories or with ignored patterns
                            if not self.should_ignore(full_path) and self.should_scan_file(full_path):
                                files_to_scan.append(full_path)
                    return files_to_scan
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                # Fall back to directory walk if git command fails
                pass

        # Fallback: recursively scan directory
        for path in root.rglob('*'):
            if path.is_file() and not self.should_ignore(path) and self.should_scan_file(path):
                files_to_scan.append(path)

        return files_to_scan
