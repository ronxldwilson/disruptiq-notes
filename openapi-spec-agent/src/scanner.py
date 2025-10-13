import os

def scan_project(project_path, ignore_paths=None):
    """Scans the project directory and returns a list of all files."""
    if ignore_paths is None:
        ignore_paths = []
    ignore_paths.extend(["__pycache__", ".git", "node_modules", "venv"])

    all_files = []
    for root, dirs, files in os.walk(project_path):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_paths]

        for file in files:
            file_path = os.path.join(root, file)
            if not any(ignore in file_path for ignore in ignore_paths):
                all_files.append(file_path)

    return all_files
