import os
import json

def detect_framework(project_path):
    """Detect the framework used in the project."""
    package_json = os.path.join(project_path, "package.json")
    if os.path.exists(package_json):
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                dependencies = data.get("dependencies", {})
                if "next" in dependencies:
                    return "nextjs"
                if "express" in dependencies:
                    return "express"
                if "fastify" in dependencies:
                    return "fastify"
        except Exception:
            pass
        pass
    # Check for other indicators
    if os.path.exists(os.path.join(project_path, "next.config.js")) or os.path.exists(os.path.join(project_path, "next.config.ts")):
        return "nextjs"
    return "unknown"

def get_api_paths(project_path, framework):
    """Get paths to scan based on framework."""
    if framework == "nextjs":
        # For Next.js, scan app/api, pages/api, src/app/api, src/pages/api directories
        api_paths = []
        for base in [project_path, os.path.join(project_path, "src")]:
            app_api = os.path.join(base, "app", "api")
            pages_api = os.path.join(base, "pages", "api")
            if os.path.exists(app_api):
                api_paths.append(app_api)
            if os.path.exists(pages_api):
                api_paths.append(pages_api)
        return api_paths
    elif framework == "express":
        # For Express, scan routes or api directories, but for now, scan common dirs
        return [os.path.join(project_path, "routes"), os.path.join(project_path, "api")]
    else:
        # Fallback: scan common API directories
        return [os.path.join(project_path, "api"), os.path.join(project_path, "routes")]

def scan_project(project_path, ignore_paths=None):
    """Scans the project directory and returns a list of relevant files."""
    print(f"Scanning project directory: {project_path}")
    if ignore_paths is None:
        ignore_paths = []
    ignore_paths.extend(["__pycache__", ".git", "node_modules", "venv"])

    framework = detect_framework(project_path)
    print(f"Detected framework: {framework}")

    api_paths = get_api_paths(project_path, framework)
    all_files = []

    if api_paths:
        # Scan only API paths
        for api_path in api_paths:
            if os.path.exists(api_path):
                for root, dirs, files in os.walk(api_path):
                    # Exclude ignored directories
                    dirs[:] = [d for d in dirs if d not in ignore_paths]
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not any(ignore in file_path for ignore in ignore_paths):
                            all_files.append(file_path)
    # No fallback: only scan API paths if they exist

    return all_files
