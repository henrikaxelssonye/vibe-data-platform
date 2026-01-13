---
name: validate
description: Run data quality checks and validation after pipeline runs or fixes. Use to verify data integrity.
---

# validate

A skill for running data quality checks and validating pipeline outputs.

## Instructions

When this skill is invoked:

### Step 1: Parse Arguments

Arguments can be:
- No args: Run all validations
- `<model_name>`: Validate specific model
- `--quick`: Run only dbt tests (skip row counts)
- `--full`: Run comprehensive checks (tests + row counts + schema)

### Step 2: Run dbt Tests

Execute dbt tests for the specified scope:

```bash
cd C:/kund/vibe-data-platform/dbt && dbt test [--select <model>]
```

Parse output for:
- Total tests run
- Pass/fail counts
- Failure details

### Step 3: Run Row Count Checks

Query DuckDB to verify data exists:

```bash
cd C:/kund/vibe-data-platform/dbt && dbt show --select <model> --limit 5
```

For each model, check:
- Row count > 0
- No unexpected NULL values in key columns
- Data freshness (if timestamps exist)

### Step 4: Schema Validation

Verify model schemas match expectations:

```sql
DESCRIBE SELECT * FROM <model>;
```

Check:
- Expected columns exist
- Data types are correct
- No unexpected columns

### Step 5: Generate Validation Report

Format results clearly:

**On Success:**
```
VALIDATION REPORT
=================

Model: orders_summary
Status: PASSED

Tests:
  [PASS] unique_customer_id
  [PASS] not_null_customer_id
  [PASS] not_null_total_revenue

Row Count: 5 rows
Key Columns: All populated

Schema Check:
  - customer_id (BIGINT) OK
  - total_orders (BIGINT) OK
  - total_revenue (DOUBLE) OK

All validations passed.
```

**On Failure:**
```
VALIDATION REPORT
=================

Model: stg_orders
Status: FAILED

Tests:
  [PASS] unique_order_id
  [FAIL] not_null_order_date - 2 rows with NULL values

Failing Rows:
  | order_id | order_date |
  |----------|------------|
  | 5        | NULL       |
  | 8        | NULL       |

Recommendation: Investigate source data for missing order dates.
```

### Step 6: Log Results

Append to `logs/pipeline_runs.log`:

```
[TIMESTAMP] VALIDATION model=orders_summary status=passed tests=3/3 rows=5
```

## Example Usage

```
/validate
```
Runs all dbt tests.

```
/validate orders_summary
```
Validates the orders_summary model specifically.

```
/validate --full
```
Runs comprehensive validation (tests + row counts + schema).

```
/validate --quick
```
Runs only dbt tests (fastest).

## Validation Checks

| Check | Description | When Used |
|-------|-------------|-----------|
| dbt tests | Schema tests defined in YAML | Always |
| Row count | Verify data exists | --full |
| NULL check | Key columns populated | --full |
| Schema match | Columns and types correct | --full |
| Freshness | Data recently updated | --full |

## Integration

This skill is called:
1. After `/apply-fix` to verify the fix worked
2. After `/run-pipeline` completes successfully
3. By pipeline-orchestrator as final verification
4. Manually by user to check data quality

## Quick Reference

```
/validate                    # All tests
/validate stg_orders         # Single model
/validate --quick            # Tests only
/validate --full             # Comprehensive
```
