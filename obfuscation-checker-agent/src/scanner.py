import os
from pathlib import Path
from typing import List, Set

class Scanner:
    def __init__(self, config):
        self.config = config
        self.ignore_patterns = set(config.get("ignore_patterns", []))
        self.scan_extensions = set(config.get("scan_extensions", []))
        self.max_file_size_mb = config.get("max_file_size_mb", 10)

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on patterns."""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False

    def should_scan_file(self, file_path: Path) -> bool:
        """Check if a file should be scanned based on extension and size."""
        if file_path.suffix.lower() not in self.scan_extensions:
            return False
        # Check file size
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                return False
        except OSError:
            return False  # Skip if can't get size
        return True

    def scan_directory(self, root_path: str) -> List[Path]:
        """Recursively scan directory and return list of files to analyze."""
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid directory path: {root_path}")

        files_to_scan = []
        for path in root.rglob('*'):
            if path.is_file() and not self.should_ignore(path) and self.should_scan_file(path):
                files_to_scan.append(path)

        return files_to_scan
