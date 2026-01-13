---
name: run-pipeline
description: Execute dbt pipeline commands and capture output. Use this skill to build, run, or test dbt models.
---

# run-pipeline

A skill for executing dbt pipeline commands with structured output and logging.

## Instructions

When this skill is invoked:

### Step 1: Parse Arguments

Determine which dbt command to run from the arguments:
- `build` (default) - Run seeds, models, and tests
- `run` - Run models only
- `test` - Run tests only
- `seed` - Load seed data only

Optional flags:
- `--select <model>` - Run specific model(s)
- `--full-refresh` - Full refresh for incremental models
- `--fail-fast` - Stop on first error

### Step 2: Execute dbt Command

Run the dbt command from the `dbt/` directory with JSON output format:

```bash
cd C:/kund/vibe-data-platform/dbt && dbt <command> [flags] --output json --output-path target/run_results.json
```

Capture both:
- Console output (for user display)
- Exit code (0 = success, non-zero = failure)

### Step 3: Parse JSON Results

After execution, read and parse `dbt/target/run_results.json` for structured data:

```python
# Key fields to extract:
{
  "elapsed_time": 4.47,           # Total duration in seconds
  "results": [
    {
      "unique_id": "model.vibe_data_platform.stg_orders",
      "status": "success",        # success, error, skipped
      "execution_time": 0.10,
      "message": "OK",
      "failures": null            # Error details if failed
    }
  ]
}
```

Calculate summary statistics:
- Total models/seeds/tests run
- Pass/fail/skip counts
- Total duration

### Step 4: Write to Log File

Append execution results to `logs/pipeline_runs.log`:

```
[2024-01-15T10:30:00] COMMAND=build STATUS=success DURATION=4.47s PASS=8 FAIL=0 SKIP=0 WARN=0
```

If there are errors, also write to `logs/errors.log`:

```
[2024-01-15T10:30:00] MODEL=stg_orders ERROR="Compilation Error: column 'order_date' not found"
```

### Step 5: Report Results to User

Format a clear summary:

**On Success:**
```
Pipeline completed successfully

Command: dbt build
Duration: 4.47s
Results: PASS=8 FAIL=0 SKIP=0

Models:
  - stg_orders (view) - OK
  - orders_summary (table) - OK

Tests: 5/5 passed
```

**On Failure:**
```
Pipeline failed

Command: dbt build
Duration: 2.31s
Results: PASS=3 FAIL=1 SKIP=4

Error in model 'stg_orders':
  Compilation Error: column 'order_date' not found in source

Suggestion: Run /diagnose to analyze this error
```

## Example Usage

```
/run-pipeline
```
Runs the full dbt build (seeds, models, tests).

```
/run-pipeline build --select orders_summary
```
Builds only the orders_summary model and its dependencies.

```
/run-pipeline test
```
Runs all dbt tests.

```
/run-pipeline run --full-refresh
```
Runs all models with full refresh.

## Log File Locations

| Log File | Purpose |
|----------|---------|
| `logs/pipeline_runs.log` | All pipeline executions |
| `logs/errors.log` | Failed runs with error details |

## Error Handling

If the pipeline fails:
1. Parse the error message from dbt output and JSON results
2. Log the error to `logs/errors.log` with timestamp and details
3. Report the error clearly to the user
4. Suggest using `/diagnose` for detailed root cause analysis

## Prerequisites

- dbt-duckdb adapter must be installed: `pip install dbt-duckdb`
- Working directory should be the project root (C:/kund/vibe-data-platform)
