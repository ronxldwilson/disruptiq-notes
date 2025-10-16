# DB Mapper — Advanced Static Repository Scanner

> **DB Mapper** is a comprehensive, enterprise-grade static analysis tool that scans software repositories to discover and map all database-related artifacts. It detects connection strings, ORM models, raw SQL queries, hardcoded secrets, migration files, schema changes, and provides data flow visualization.

This README describes the advanced features, installation, usage, detection capabilities, and extensibility of the project.

## Table of Contents

1. Project Overview
2. Goals & Non-goals
3. High-level Workflow
4. Design Principles
5. Architecture & Modules (Modular by design)
6. Detection Techniques & Heuristics
7. Supported Languages & Frameworks (out of the box)
8. CLI & Usage Examples
9. Configuration
10. Output Formats & Examples
11. Quality, Tests & Benchmarks
12. Security & Privacy Considerations
13. Extending the Scanner (Plugins & Rules)
14. Packaging & Distribution Recommendations
15. Contributing Guide
16. Roadmap & TODOs
17. License

---

## Project Overview

DB Mapper is a **static DB mapping tool** that analyzes source code and repository files (including configuration, IaC, and migration files) *without executing them*, to locate and classify database-related artifacts.

It outputs:

* **Database Connections**: DSN detection, environment variables, provider identification
* **ORM Models**: Django, SQLAlchemy, Sequelize, TypeORM, JPA/Hibernate, ActiveRecord, GORM
* **Raw SQL Queries**: Inline SQL detection with context and risk assessment
* **Secret Detection**: API keys, tokens, passwords, private keys, JWT tokens, AWS credentials
* **Migration Files**: Django, Alembic, Flyway, Liquibase, Rails migrations
* **Schema Changes**: CREATE/ALTER/DROP TABLE statements across frameworks
* **Data Flow Visualization**: Graphviz DOT files showing relationships between components
* **Multiple Output Formats**: JSON, CSV, HTML reports, and interactive graphs
* **Cross-file Analysis**: Model-to-query mapping and relationship inference

---

## Goals & Non-goals

### Goals

* Accurate static discovery of DB touchpoints
* Modular, language-extensible detectors
* Safe operation — no runtime execution
* Machine-readable reports

### Non-goals

* No runtime tracing or query capture
* No automatic schema or migration manipulation
* Not a replacement for full data lineage systems

---

## High-level Workflow

1. **Input Processing**: Accept repository path with flexible filtering options.
2. **Intelligent File Discovery**: Multi-language file detection with extension and content-based heuristics.
3. **Advanced Parsing**: Regex-based pattern matching with AST support for complex analysis.
4. **Comprehensive Detection**:
   - Connection strings and environment variables
   - ORM models across multiple frameworks
   - Raw SQL queries with risk assessment
   - Hardcoded secrets and credentials
   - Migration files and schema changes
5. **Relationship Analysis**: Cross-file mapping between models, queries, and migrations.
6. **Risk Assessment**: Confidence scoring and severity classification for findings.
7. **Multiple Outputs**: JSON, CSV, HTML reports, and Graphviz visualization.

---

## Design Principles

* **Modular:** Add or remove detectors easily.
* **Language-first:** Use ASTs where possible, regex fallback otherwise.
* **Deterministic:** Identical input = identical results.
* **Configurable:** Fine-tune confidence, languages, and detectors.
* **Explainable:** Each finding includes evidence and confidence.

---

## Architecture & Modules

Recommended project layout:

```
db-mapper/
├── README.md
├── pyproject.toml
├── src/
│   ├── dbmapper/
│   │   ├── __main__.py         # CLI entry
│   │   ├── cli.py              # Argparse interface
│   │   ├── runner.py           # Core orchestrator
│   │   ├── scanner/            # File discovery
│   │   ├── parsers/            # AST / regex parsers
│   │   ├── detectors/          # DB/ORM/SQL detectors
│   │   ├── crosslinker/        # Model-query mapping
│   │   ├── normalizers/        # Normalize DSNs, providers
│   │   ├── output/             # Writers (JSON, HTML, Graph)
│   │   ├── plugins/            # Optional extensions
│   │   ├── rules/              # Rule signatures
│   │   └── utils/
│   └── tests/
└── docs/
```

---

## Core Components

**File discovery**
Walks repo, filters relevant files, detects languages.

**Parsers**
Wraps ASTs or uses text-based regex scanning.

**Detectors**

* `connection_detector`: DSN patterns, environment variables, provider normalization
* `orm_detector`: Multi-framework ORM model detection (Django, SQLAlchemy, Sequelize, TypeORM, JPA, ActiveRecord, GORM)
* `raw_sql_detector`: Inline SQL queries with context and risk assessment
* `secret_detector`: API keys, tokens, passwords, private keys, JWT, AWS credentials with allowlist filtering
* `migration_detector`: Framework-specific migration detection (Django, Alembic, Flyway, Liquibase, Rails)
* `schema_detector`: Database schema changes and DDL statements

**Crosslinker**
Connects models and their usage in queries or services.

**Normalizers**
Canonicalizes connection URIs (e.g., all postgres variants → `postgresql`).

**Output Writers**

* JSON
* HTML (searchable, human-readable)
* Graphviz for visual data flows

**Plugins**
Third-party detectors added via plugin entry points.

---

## Detection Techniques & Heuristics

**Connection Detection**

* Regex match for DSNs like `postgres://`, `mysql://`
* Env variable lookups (`DB_URL`, `DATABASE_URL`)
* YAML/Terraform/Docker configs referencing DBs

**ORM Detection**

* Identify base classes (`class User(models.Model)`)
* Imports of ORM libs (SQLAlchemy, Sequelize, etc.)

**Raw SQL Detection**

* Regex for common SQL patterns (`SELECT`, `INSERT`, etc.)
* AST scan for `execute()` calls with literal SQL strings

**Migration Detection**

* Recognize framework-specific directories
* Parse for `create_table`, `add_column` patterns

**Secret Detection**

* Regexes for passwords, keys, base64 strings
* Avoid false positives using allowlists

---

## Supported Languages & Frameworks

Comprehensive multi-language support:

**Python**
* Django ORM, SQLAlchemy, Peewee
* Raw SQL queries, connection strings
* Alembic migrations, custom migration scripts

**JavaScript/TypeScript**
* Sequelize, TypeORM, Mongoose, Prisma
* Node.js database drivers, connection pooling
* GraphQL resolvers with database access

**Java**
* JPA/Hibernate, Spring Data JDBC
* MyBatis, jOOQ for type-safe SQL
* Flyway/Liquibase migrations

**Ruby**
* ActiveRecord (Rails), Sequel, ROM
* Sinatra/DataMapper applications
* Rails migrations and database tasks

**Go**
* GORM, database/sql driver
* Buntdb, Storm, custom ORM libraries
* Migration tools and schema management

**SQL & Database Scripts**
* Plain SQL files, stored procedures
* Database migration scripts
* Schema definition files

**Infrastructure & Configuration**
* Docker Compose database services
* Terraform AWS RDS, GCP Cloud SQL
* Kubernetes ConfigMaps and Secrets
* Environment files (.env, .env.local)
* YAML/TOML/JSON configuration files

---

## CLI & Usage Examples

**Basic Scan**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
db-mapper scan /path/to/repo --output findings.json
```

**Flags**

```
--path PATH                Repository path (required)
--output FILE              Output file base name (default: findings)
--formats json,csv,html,graph  Output formats (default: json)
--include GLOB             Glob patterns for files to include
--exclude GLOB             Glob patterns for files to exclude
--languages python,js,java,ruby,go,sql  Limit to specific languages
--plugins PLUGINS          Enable additional detector plugins
--min-confidence FLOAT     Filter results below confidence threshold (default: 0.5)
--verbose                  Enable verbose logging
--threads N                Number of parallel worker threads (default: 4)
--config FILE              Path to YAML configuration file
```

**Sample Output (JSON)**

```json
{
  "summary": {"files_scanned": 142, "findings": 29},
  "findings": [
    {
      "id": "f-0001",
      "type": "connection",
      "provider": "postgresql",
      "file": "config/.env",
      "line": 12,
      "evidence": ["DATABASE_URL=postgres://user:pass@db:5432/app"],
      "confidence": 0.98
    },
    {
      "id": "f-0002",
      "type": "orm_model",
      "framework": "django",
      "file": "models/user.py",
      "evidence": ["class User(models.Model):"],
      "confidence": 0.95
    }
  ]
}
```

---

## Configuration Example (`dbmapper.yml`)

```yaml
include:
  - "**/*.py"
  - "**/*.sql"
exclude:
  - "**/node_modules/**"
  - "**/.venv/**"
languages:
  - python
  - javascript
detectors:
  connection_detector: true
  orm_detector: true
  raw_sql_detector: true
  secret_detector: false
output:
  json: findings.json
  html: report.html
confidence_threshold: 0.5
```

---

## Output Formats

* **JSON:** Structured data with full metadata, confidence scores, and relationships
* **CSV:** Tabular format for import into spreadsheets, SIEM systems, or databases
* **HTML:** Interactive web report with filtering, sorting, and severity highlighting
* **Graphviz/DOT:** Visual data flow diagrams showing connections between components

### Enhanced JSON Schema

```json
{
  "summary": {
    "files_scanned": 150,
    "findings": 45,
    "high_severity": 3,
    "medium_severity": 12,
    "low_severity": 30
  },
  "findings": [
    {
      "id": "f-0001",
      "type": "secret",
      "secret_type": "aws_access_key",
      "severity": "high",
      "file": "config/production.py",
      "line": 25,
      "evidence": ["AWS_ACCESS_KEY_ID = \"AKIAIOSFODNN7EXAMPLE\""],
      "confidence": 0.95,
      "framework": null,
      "description": "AWS Access Key ID detected"
    }
  ]
}
```

---

## Quality & Testing

* Unit tests per detector
* End-to-end repo tests
* Benchmark scanning performance
* Type checks (mypy/tsc)
* CI/CD integration with GitHub Actions

---

## Security & Privacy

* No code execution
* Mask credentials in output
* Never upload code externally without consent
* Optional `--show-secrets` for controlled exposure

---

## Extending the Scanner

**Plugin Model**

* Plugins expose a `register(detector_registry)` API
* Discoverable via entry points in `pyproject.toml`

**Writing a Detector**
Implement detector functions that return findings:

```python
def detect_custom_patterns(content: str, file_path: Path) -> List[Dict[str, Any]]:
    """Example custom detector for specific patterns."""
    findings = []
    # Your detection logic here
    return findings
```

Each finding includes:
- `id`: Unique identifier
- `type`: Detection type (connection, orm_model, raw_sql, secret, migration, schema_change)
- `file`: File path
- `line`: Line number
- `evidence`: Code snippets showing the finding
- `confidence`: Confidence score (0.0-1.0)
- `severity`: Risk level (high/medium/low)
- Additional type-specific fields

**Rule Pack Example**

```yaml
- id: R001
  name: Postgres DSN
  pattern: '(?i)postgres(?:ql)?://[\\w:@\\-\\.\\/%\\?=~&]+'
  description: 'Matches PostgreSQL connection strings'
  risk: high
  default_confidence: 0.7
```

---

## Packaging & Distribution

* Avoid `.egg` packaging.
* Use modern tooling: `poetry`, `flit`, or `setuptools` with wheels.
* Define CLI entry in `pyproject.toml`:

```toml
[project.scripts]
db-mapper = "dbmapper.__main__:main"
```

---

## Contributing

1. Fork repo and create a feature branch.
2. Run tests locally.
3. Add fixtures for any new detector or pattern.
4. Document new modules or CLI flags.
5. Submit PR with clear changelog entry.

---

## Roadmap & Future Enhancements

### ✅ **Implemented**
* Multi-language framework support (Python, JS/TS, Java, Ruby, Go, SQL)
* Secret detection with allowlist filtering
* Migration file detection across frameworks
* Graphviz visualization with relationship mapping
* CSV export for enterprise integration
* Risk scoring and severity classification
* Parallel processing capabilities

### 🔄 **In Development**
* AST-based parsing for improved accuracy
* Plugin system for custom detectors
* Configuration file support (YAML)
* Interactive HTML reports with filtering

### 🚀 **Planned Features**
* Tree-sitter integration for advanced language parsing
* SQL AST analysis for column-level data flow
* CI/CD integration with GitHub Actions, Jenkins
* Cloud provider detection (AWS RDS, GCP Cloud SQL, Azure Database)
* GUI application for interactive analysis
* Real-time monitoring and alerting
* Integration with security scanners (SAST, DAST)
* Support for additional languages (C#, PHP, Kotlin, Rust)
* Machine learning-based pattern recognition
* Compliance reporting (GDPR, HIPAA, SOX)

---

## Appendix — Useful Regex Patterns

**Generic DSN**

```
(?i)(postgres(?:ql)?|mysql|mariadb|mongodb|sqlite|mssql)://[\\w:@\\-\\.\\/%\\?=~&]+
```

**ENV Variable**

```
(?m)^(DB_URL|DATABASE_URL|[A-Z_]*DB[A-Z_]*)\\s*=\\s*(.+)$
```

**SQL Detection**

```
(?is)(SELECT|INSERT|UPDATE|DELETE|CREATE\\s+TABLE|ALTER\\s+TABLE)\\s+.+?
```

---

## JSON Schema (Simplified)

```json
{
  "type": "object",
  "properties": {
    "summary": {"type": "object"},
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "type": {"type": "string"},
          "file": {"type": "string"},
          "line": {"type": "integer"},
          "evidence": {"type": "array"},
          "confidence": {"type": "number"}
        }
      }
    }
  }
}
```
