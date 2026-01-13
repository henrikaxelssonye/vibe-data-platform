# Plan: Agentic Data Platform

> **Status**: Implemented
> **Created**: 2026-01-13
> **Completed**: 2026-01-13
> **Plan ID**: 001

## Summary

Build a self-healing data platform using dbt + DuckDB, orchestrated by Claude agents. The platform runs pipelines, detects errors, proposes/applies fixes, and retries automatically. Supports both autonomous and human-in-loop execution modes, with extensible data source ingestion from files and APIs.

## Goals

- [x] Pipeline triggered and run by an agent
- [x] Agent monitors pipeline status and checks for errors
- [x] Agent suggests fixes, implements and retries on failure
- [x] Log all executions in structured log files
- [x] Support autonomous and human-in-loop modes
- [x] Extensible data source support (CSV, Parquet, JSON, API)

## Non-Goals

- Real-time streaming (future enhancement)
- External database connections (configuration ready, not implemented)
- Scheduled/automated pipeline runs (manual trigger only)
- Web UI dashboard

## Architecture

### Overview

An agent-orchestrated data platform where Claude agents coordinate dbt pipeline execution with self-healing capabilities.

```
User Request --> Pipeline Orchestrator Agent
                        |
        +---------------+---------------+
        |               |               |
   /run-pipeline   /diagnose       /apply-fix
        |               |               |
        v               v               v
    dbt build    Diagnostician    File backup
    DuckDB       Agent            + edit
        |               |               |
        +--------> Logs <--------------+
```

### Components

| Component | Purpose |
|-----------|---------|
| `pipeline-orchestrator` | Main agent coordinating pipeline runs with retry logic |
| `diagnostician` | Specialized agent for error analysis and fix proposals |
| `/run-pipeline` | Skill to execute dbt commands |
| `/diagnose` | Skill to analyze errors |
| `/apply-fix` | Skill to apply fixes with backup |
| `/validate` | Skill for data quality checks |
| `ingest_files.py` | Script for CSV/Parquet/JSON ingestion |
| `extract_api.py` | Script for API data extraction |

### Data Flow

```
Data Sources          Ingestion           dbt Pipeline         Output
─────────────         ─────────           ────────────         ──────
CSV/Parquet  ───┐
JSON files   ───┼──▶  ingest_files.py ──▶ staging views ──▶ mart tables ──▶ DuckDB
API endpoints───┘     extract_api.py      (stg_*)           (summary)
                                              │
                                              ▼
                                    Self-Healing Loop
                                    (diagnose → fix → retry)
```

### Self-Healing Loop

```
1. Run pipeline (/run-pipeline)
      |
      v
2. Check result
      |
   Success? --> Log success, report to user, DONE
      |
      No
      v
3. Diagnose error (/diagnose)
      |
      v
4. Generate fix proposal with confidence score
      |
      v
5. Check mode:
   - autonomous + confidence >= 80% --> Apply fix automatically
   - human-in-loop --> Present fix, ask for approval
      |
      v
6. Apply fix if approved (/apply-fix)
      |
      v
7. Retry (max 3 attempts with exponential backoff)
```

## Implementation Phases

### Phase 1: Foundation

**Goal**: Minimal working pipeline with dbt + DuckDB

1. Initialize dbt project with DuckDB adapter
2. Create `dbt/profiles.yml` with DuckDB config
3. Add `dbt/seeds/sample_orders.csv` (10 rows sample data)
4. Create `dbt/models/staging/stg_orders.sql`
5. Create `dbt/models/marts/orders_summary.sql`
6. Create `/run-pipeline` skill (basic dbt execution)
7. Set up `logs/` directory

**Verification**: Run `dbt build` successfully

### Phase 2: Observability

**Goal**: Structured logging and error capture

1. Enhance `/run-pipeline` to parse dbt JSON output
2. Implement structured logging to `logs/pipeline_runs.log`
3. Create `/diagnose` skill (parse common dbt errors)
4. Create `config/execution_mode.yml`

**Verification**: Failed builds produce structured error logs

### Phase 3: Self-Healing Core

**Goal**: Autonomous error recovery

1. Create `pipeline-orchestrator` agent
2. Create `diagnostician` agent
3. Create `/apply-fix` skill with backup mechanism
4. Implement retry logic with exponential backoff

**Verification**: Introduce error, watch agent fix and retry

### Phase 4: Human-in-Loop Mode

**Goal**: Approval workflow for fixes

1. Add fix proposal presentation with diff view
2. Add approval workflow in `/apply-fix`
3. Create `/validate` skill for post-fix checks
4. Test mode toggle (autonomous vs human-in-loop)

**Verification**: Error triggers approval prompt, fix applied after approval

### Phase 5: Data Sources

**Goal**: Multiple data ingestion patterns

1. Create `config/sources.yml` source registry
2. Create `scripts/ingest_files.py` for CSV/Parquet/JSON
3. Create `scripts/extract_api.py` for API extraction
4. Add sample data files (customers, products)
5. Create new dbt models (stg_customers, stg_products, customer_orders)
6. Update documentation

**Verification**: Ingest files, run expanded pipeline

## Files Created

| File | Purpose |
|------|---------|
| `dbt/dbt_project.yml` | dbt configuration |
| `dbt/profiles.yml` | DuckDB connection |
| `dbt/seeds/sample_orders.csv` | Sample order data |
| `dbt/models/sources.yml` | External source definitions |
| `dbt/models/staging/stg_orders.sql` | Staged orders |
| `dbt/models/staging/stg_orders.yml` | Schema + tests |
| `dbt/models/staging/stg_customers.sql` | Staged customers |
| `dbt/models/staging/stg_products.sql` | Staged products |
| `dbt/models/marts/orders_summary.sql` | Order aggregations |
| `dbt/models/marts/customer_orders.sql` | Customer profiles |
| `.claude/agents/pipeline-orchestrator.md` | Main orchestrator |
| `.claude/agents/diagnostician.md` | Error analysis |
| `.claude/skills/run-pipeline/SKILL.md` | Pipeline execution |
| `.claude/skills/diagnose/SKILL.md` | Error diagnosis |
| `.claude/skills/apply-fix/SKILL.md` | Fix application |
| `.claude/skills/validate/SKILL.md` | Data validation |
| `config/execution_mode.yml` | Pipeline behavior |
| `config/sources.yml` | Data source registry |
| `scripts/ingest_files.py` | File ingestion |
| `scripts/extract_api.py` | API extraction |
| `data/raw/customers.csv` | Sample customers |
| `data/raw/products.csv` | Sample products |
| `logs/.gitkeep` | Logs directory |
| `CLAUDE.md` | Project documentation |

## Dependencies

- `dbt-duckdb` - dbt adapter for DuckDB
- `pyyaml` - YAML parsing for configs
- `requests` - API extraction

## Configuration

### execution_mode.yml

```yaml
execution:
  mode: human-in-loop  # or "autonomous"

retry:
  max_retries: 3
  base_delay_seconds: 5
  backoff_multiplier: 2

autonomous:
  min_confidence: 0.8
  create_backups: true
```

### sources.yml

```yaml
sources:
  files:
    csv:
      enabled: true
      path: data/raw/
      pattern: "*.csv"
    parquet:
      enabled: true
      path: data/raw/
      pattern: "*.parquet"
  apis:
    jsonplaceholder:
      enabled: true
      base_url: "https://jsonplaceholder.typicode.com"
      endpoints:
        - name: posts
          path: /posts
```

## Verification

### Final Pipeline Test

```bash
# Ingest data
python scripts/ingest_files.py --all

# Run full pipeline
cd dbt && dbt build

# Expected: PASS=11 FAIL=0
```

### Self-Healing Test

1. Introduce error in model (e.g., wrong column name)
2. Run `/run-pipeline`
3. Observe error detection and diagnosis
4. In human-in-loop: Approve fix
5. In autonomous: Watch auto-fix
6. Verify pipeline recovers

## Future Enhancements

- Real-time streaming sources
- External database connections
- Scheduled pipeline runs
- Web UI dashboard
- Data lineage visualization
- Alerting integrations

---

## Implementation Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-13 | Phase 1 | Foundation complete - dbt + DuckDB working |
| 2026-01-13 | Phase 2 | Observability complete - logging and /diagnose |
| 2026-01-13 | Phase 3 | Self-healing complete - agents and retry logic |
| 2026-01-13 | Phase 4 | Human-in-loop complete - approval workflow |
| 2026-01-13 | Phase 5 | Data sources complete - CSV/API ingestion |
