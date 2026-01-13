# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Vibe Data Platform is an agentic data platform using dbt + DuckDB, orchestrated by Claude agents. The platform can run pipelines, detect errors, propose/apply fixes, and retry automatically.

## Project Structure

```
vibe-data-platform/
├── .claude/
│   ├── agents/
│   │   ├── pipeline-orchestrator.md  # Main pipeline coordinator
│   │   ├── diagnostician.md          # Error analysis specialist
│   │   └── simple-demo.md            # Test agent
│   └── skills/
│       ├── run-pipeline/             # Execute dbt pipelines
│       ├── diagnose/                 # Analyze errors
│       ├── apply-fix/                # Apply fixes with backup
│       └── validate/                 # Data quality checks
├── .github/
│   └── workflows/
│       ├── pipeline.yml              # Basic scheduled workflow
│       └── agentic-pipeline.yml      # Claude-powered self-healing workflow
├── azure/
│   ├── setup.sh                      # Provision Azure resources
│   ├── teardown.sh                   # Remove Azure resources
│   ├── setup-logic-app.sh            # Deploy email Logic App
│   └── credentials.template.env      # Template for credentials
├── plans/
│   ├── README.md                     # Plan index and guidelines
│   ├── TEMPLATE.md                   # Template for new plans
│   ├── proposed/                     # Plans awaiting approval
│   └── implemented/                  # Completed plans
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml                  # DuckDB connection (dev + azure targets)
│   ├── macros/
│   │   └── azure_httpfs.sql          # Azure blob storage macros
│   ├── seeds/                        # Seed data (CSV)
│   └── models/
│       ├── sources.yml               # External source definitions
│       ├── staging/                  # Staging models (views)
│       └── marts/                    # Mart models (tables)
├── data/
│   ├── raw/                          # Source files (CSV, Parquet, JSON)
│   └── processed/                    # DuckDB database
├── logs/
│   ├── pipeline_runs.log             # Execution history
│   ├── errors.log                    # Error details
│   └── fixes.log                     # Applied fixes audit
├── config/
│   ├── execution_mode.yml            # Pipeline behavior config
│   ├── sources.yml                   # Data source registry (local + Azure)
│   ├── github_actions.yml            # Workflow configuration
│   └── notifications.yml             # Alert channel settings
└── scripts/
    ├── extract_api.py                # API data extraction
    ├── ingest_files.py               # File ingestion (local + Azure)
    ├── upload_to_azure.py            # Upload data to Azure
    └── sync_azure.py                 # Bidirectional Azure sync
```

## Available Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `pipeline-orchestrator` | opus | Main coordinator with self-healing loop |
| `diagnostician` | sonnet | Deep error analysis and fix proposals |
| `simple-demo` | opus | Test agent system functionality |

## Available Skills

| Skill | Description |
|-------|-------------|
| `/run-pipeline [cmd]` | Execute dbt pipeline (build, run, test, seed) |
| `/diagnose [error]` | Analyze errors and propose fixes |
| `/apply-fix [--auto]` | Apply fixes with backup and verification |
| `/validate [model]` | Run data quality checks |

## Data Sources

### File Ingestion

```bash
# List available files
python scripts/ingest_files.py --list

# Ingest all files
python scripts/ingest_files.py --all

# Ingest specific file
python scripts/ingest_files.py --file customers.csv

# Show file schema
python scripts/ingest_files.py --schema customers.csv
```

Supported formats: CSV, Parquet, JSON

### API Extraction

```bash
# List configured APIs
python scripts/extract_api.py --list

# Extract from all enabled APIs
python scripts/extract_api.py

# Extract specific API
python scripts/extract_api.py --api jsonplaceholder
```

Configure APIs in `config/sources.yml`.

## dbt Commands

```bash
# Run full pipeline
cd dbt && dbt build

# Run specific model
cd dbt && dbt run --select customer_orders

# Run tests
cd dbt && dbt test

# Show model data
cd dbt && dbt show --select customer_orders
```

## dbt Models

| Model | Type | Description |
|-------|------|-------------|
| `stg_orders` | staging/view | Staged orders with line totals |
| `stg_customers` | staging/view | Staged customer data |
| `stg_products` | staging/view | Staged product catalog |
| `orders_summary` | marts/table | Customer order aggregations |
| `customer_orders` | marts/table | Customer profile with orders |

## Configuration

### execution_mode.yml

Controls pipeline behavior:
- `mode`: "autonomous", "human-in-loop", or "autonomous-ci"
- `max_retries`: Retry attempts (default: 3)
- `min_confidence`: Threshold for auto-fix (0.8 local, 0.7 CI)
- `auto_detect_ci`: Auto-switch to CI mode in GitHub Actions (default: true)
- `ci.commit_strategy`: How to handle fixes in CI ("none", "direct", "pr")

### sources.yml

Defines data sources:
- File sources (CSV, Parquet, JSON paths)
- API sources (endpoints, auth, rate limits)
- Database sources (connection settings)

## Self-Healing Workflow

```
/run-pipeline --> Error? --> /diagnose --> /apply-fix --> /run-pipeline (retry)
```

**Autonomous mode:** Auto-applies fixes with confidence >= 80%
**Human-in-loop mode:** Requires approval before applying fixes

## Log Files

| File | Purpose |
|------|---------|
| `logs/pipeline_runs.log` | All pipeline executions |
| `logs/errors.log` | Failed runs with error details |
| `logs/fixes.log` | Applied fixes audit trail |

## Adding New Data Sources

1. **CSV/Parquet files:** Place in `data/raw/`, run `python scripts/ingest_files.py`
2. **API sources:** Add config to `config/sources.yml`, run `python scripts/extract_api.py`
3. **Create dbt source:** Add to `dbt/models/sources.yml`
4. **Create staging model:** Add SQL to `dbt/models/staging/`
5. **Run pipeline:** `dbt build`

## Agent Planning

All new features must have a plan before implementation.

### Plan Structure

```
plans/
├── README.md           # Index and guidelines
├── TEMPLATE.md         # Template for new plans
├── proposed/           # Plans awaiting approval
└── implemented/        # Completed plans (archive)
```

### Planning Workflow

1. **Create Plan**: Copy `TEMPLATE.md` to `proposed/NNN-feature-name.md`
2. **Fill Sections**: Summary, goals, architecture, phases, files, verification
3. **Review**: Present plan to user for approval
4. **Implement**: Execute phases, track progress
5. **Archive**: Move completed plan to `implemented/`

### Plan Naming

```
NNN-short-description.md
```

Examples: `001-agentic-platform.md`, `002-streaming-sources.md`

### Required Sections

- **Summary**: One-paragraph overview
- **Goals**: Success criteria (checkboxes)
- **Architecture**: Technical design with diagrams
- **Implementation Phases**: Step-by-step breakdown
- **Files to Create/Modify**: Explicit file list
- **Verification**: How to test completion
- **Implementation Log**: Date-stamped progress

### Referencing Plans

In code or commits:
```
# See: plans/implemented/001-agentic-platform.md
```

## Conventions

- dbt models follow staging -> marts pattern
- Staging models are views, marts are tables
- Raw tables prefixed with `raw_`
- All fixes create backups before modifying
- Logs use structured format with timestamps
- All features require a plan before implementation

## Azure Integration

The platform supports Azure Blob Storage for cloud persistence and GitHub Actions for scheduled execution.

### Azure Setup

```bash
# Provision Azure resources (Storage Account, containers, Service Principal)
./azure/setup.sh [resource-group] [location]

# Remove all Azure resources
./azure/teardown.sh [resource-group]

# Set up email notifications via Logic App
./azure/setup-logic-app.sh [resource-group] [location] [email]
```

### Azure Storage Containers

| Container | Purpose |
|-----------|---------|
| `raw` | Source data files (CSV, Parquet, JSON) |
| `duckdb` | DuckDB database file |
| `logs` | Pipeline execution logs |

### Data Sync Commands

```bash
# Upload all data to Azure
python scripts/upload_to_azure.py --all

# Download data from Azure (for local development)
python scripts/sync_azure.py --download

# Check sync status
python scripts/sync_azure.py --status

# Ingest files and upload to Azure
python scripts/ingest_files.py --azure
```

### dbt Targets

| Target | Usage |
|--------|-------|
| `dev` | Local development (default) |
| `azure` | Cloud execution with httpfs extension |

```bash
# Run locally
cd dbt && dbt build

# Run with Azure (reads from blob storage)
cd dbt && dbt build --target azure
```

## Scheduled Execution

Pipeline runs are scheduled via GitHub Actions. Two workflows are available:

| Workflow | File | Description |
|----------|------|-------------|
| Basic | `pipeline.yml` | Simple dbt execution, fails on error |
| Agentic | `agentic-pipeline.yml` | Claude-powered self-healing pipeline |

### Agentic Pipeline (Recommended)

The agentic workflow uses `anthropics/claude-code-action` to run pipelines with intelligent self-healing:

```
┌─────────────────────────────────────────────────────────────┐
│                 Claude Pipeline Orchestrator                 │
│                                                             │
│  1. Run dbt build                                           │
│  2. If error → /diagnose → /apply-fix → retry (max 3x)     │
│  3. If unrecoverable → Create detailed GitHub Issue         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Automatic error diagnosis and fix application
- Up to 3 retry attempts with exponential backoff
- Detailed root cause analysis in GitHub Issues
- Lower noise - only creates issues for truly unresolvable errors

### Schedule Configuration

Default: Daily at 6:00 AM UTC. Configure in workflow file:

```yaml
schedule:
  - cron: '0 6 * * *'      # Daily at 6 AM UTC
  - cron: '0 */4 * * *'    # Every 4 hours
  - cron: '0 6 * * 1-5'    # Weekdays only
```

### Manual Trigger

```bash
# Trigger agentic pipeline (recommended)
gh workflow run agentic-pipeline.yml

# With options
gh workflow run agentic-pipeline.yml -f dbt_command=build -f max_retries=3

# Trigger basic pipeline (no self-healing)
gh workflow run pipeline.yml
```

### Required GitHub Secrets

| Secret | Description | Required For |
|--------|-------------|--------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Agentic workflow |
| `AZURE_STORAGE_ACCOUNT` | Storage account name | Both workflows |
| `AZURE_STORAGE_KEY` | Storage account access key | Both workflows |
| `LOGIC_APP_EMAIL_URL` | Logic App webhook | Optional |
| `NOTIFICATION_WEBHOOK_URL` | Teams/Slack webhook | Optional |

### Execution Modes

Configure in `config/execution_mode.yml`:

| Mode | Description | Use Case |
|------|-------------|----------|
| `human-in-loop` | Requires approval for fixes | Local development |
| `autonomous` | Auto-applies high-confidence fixes | Trusted automation |
| `autonomous-ci` | Full autonomous with CI optimizations | GitHub Actions |

The agentic workflow automatically uses `autonomous-ci` mode when `auto_detect_ci: true`.

### Notifications

On failure (after self-healing attempts exhausted):
- **GitHub Issues**: Auto-created with detailed RCA and labels
- **Email**: Via Azure Logic App (if configured)
- **Webhook**: Teams or Slack (if configured)

Configure in `config/notifications.yml`.

## Agentic Self-Healing

The platform implements intelligent self-healing using Claude agents.

### How It Works

```
Error Occurs
    │
    ▼
┌─────────────────┐
│   /diagnose     │  ← Analyze error, classify type, find root cause
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /apply-fix     │  ← Generate fix, create backup, apply change
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /validate      │  ← Verify fix worked, check data quality
└────────┬────────┘
         │
    Success? ──No──► Retry (up to max_retries)
         │
        Yes
         │
         ▼
      Complete
```

### Error Classification

The diagnostician agent classifies errors:

| Type | Pattern | Auto-Fix Confidence |
|------|---------|---------------------|
| SCHEMA | Column not found | High (85-95%) |
| SYNTAX | Compilation error | High (80-90%) |
| MISSING_REF | Relation doesn't exist | Medium (70-85%) |
| DATA_QUALITY | Test failure | Medium (60-80%) |
| DATABASE | DuckDB error | Low (40-60%) |

### Confidence Thresholds

- **>= 0.8**: Auto-apply in `autonomous` mode
- **>= 0.7**: Auto-apply in `autonomous-ci` mode
- **< threshold**: Requires human approval or creates issue

### Audit Trail

All actions are logged:
- `logs/pipeline_runs.log`: Execution history
- `logs/errors.log`: Error details and diagnosis
- `logs/fixes.log`: Applied fixes with timestamps and confidence scores
