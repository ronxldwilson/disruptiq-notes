#!/usr/bin/env python3
"""File discovery module for scanning repositories."""

import fnmatch
from pathlib import Path
from typing import List, Optional


# Language detection by file extensions
LANGUAGE_EXTENSIONS = {
    "python": [".py", ".pyx", ".pyw"],
    "javascript": [".js", ".jsx", ".ts", ".tsx", ".mjs"],
    "java": [".java"],
    "csharp": [".cs", ".vb"],
    "php": [".php"],
    "ruby": [".rb"],
    "go": [".go"],
    "sql": [".sql"],
    "yaml": [".yml", ".yaml"],
    "json": [".json"],
    "xml": [".xml"],
    "ini": [".ini", ".cfg", ".conf"],
    "env": [".env"],
    "docker": ["Dockerfile", ".dockerfile"],
    "terraform": [".tf", ".tfvars"],
}


def discover_files(
    repo_path: Path,
    include_patterns: List[str],
    exclude_patterns: List[str],
    languages: Optional[List[str]] = None,
) -> List[Path]:
    """Discover files in the repository matching the criteria.

    Args:
        repo_path: Root path of the repository
        include_patterns: Glob patterns to include
        exclude_patterns: Glob patterns to exclude
        languages: List of languages to filter by (None for all)

    Returns:
        List of matching file paths
    """
    if not repo_path.exists() or not repo_path.is_dir():
        raise ValueError(f"Repository path {repo_path} does not exist or is not a directory")

    # If no languages specified, include all
    allowed_extensions = set()
    if languages:
        for lang in languages:
            if lang in LANGUAGE_EXTENSIONS:
                allowed_extensions.update(LANGUAGE_EXTENSIONS[lang])
    else:
        # Include all known extensions
        for exts in LANGUAGE_EXTENSIONS.values():
            allowed_extensions.update(exts)

    # Also include common config files
    allowed_extensions.update(LANGUAGE_EXTENSIONS["yaml"])
    allowed_extensions.update(LANGUAGE_EXTENSIONS["json"])
    allowed_extensions.update(LANGUAGE_EXTENSIONS["ini"])
    allowed_extensions.update(LANGUAGE_EXTENSIONS["env"])
    allowed_extensions.update(LANGUAGE_EXTENSIONS["docker"])
    allowed_extensions.update(LANGUAGE_EXTENSIONS["terraform"])

    files = []
    for pattern in include_patterns:
        # Use rglob for glob patterns
        for path in repo_path.rglob(pattern):
            if path.is_file():
                # Check exclude patterns
                if any(fnmatch.fnmatch(str(path), excl) for excl in exclude_patterns):
                    continue

                # Check extension
                if allowed_extensions and path.suffix not in allowed_extensions:
                    # Check for exact filename matches (like Dockerfile)
                    if path.name not in allowed_extensions:
                        continue

                files.append(path)

    return files
