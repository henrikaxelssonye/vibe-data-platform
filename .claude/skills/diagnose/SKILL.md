---
name: diagnose
description: Analyze dbt pipeline errors and propose fixes. Use after a pipeline failure to understand root cause.
---

# diagnose

A skill for analyzing dbt pipeline errors and proposing fixes.

## Instructions

When this skill is invoked:

### Step 1: Gather Error Context

Collect information about the failure:

1. **Read recent errors from logs:**
   ```bash
   tail -20 logs/errors.log
   ```

2. **Read dbt run results:**
   ```bash
   cat dbt/target/run_results.json
   ```

3. **Check dbt compile output for syntax errors:**
   ```bash
   cd C:/kund/vibe-data-platform/dbt && dbt compile 2>&1
   ```

If the user provides a specific error message, use that directly.

### Step 2: Classify the Error

Identify the error type from common dbt error patterns:

| Error Pattern | Classification | Common Cause |
|---------------|----------------|--------------|
| `Compilation Error` | SYNTAX | Invalid SQL or Jinja |
| `column "X" not found` | SCHEMA | Column renamed or removed in source |
| `relation "X" does not exist` | MISSING_REF | Referenced model doesn't exist |
| `Database Error` | DATABASE | DuckDB execution failure |
| `Parsing Error` | YAML | Invalid YAML in schema files |
| `Test failure` | DATA_QUALITY | Data doesn't meet test criteria |
| `Could not find source` | SOURCE | Source not defined or misspelled |

### Step 3: Investigate Root Cause

Based on error type, perform targeted investigation:

**For SCHEMA errors (column not found):**
1. Read the failing model SQL file
2. Query DuckDB to check actual schema:
   ```sql
   DESCRIBE SELECT * FROM <source_table>;
   ```
3. Compare expected vs actual columns

**For SYNTAX errors:**
1. Read the failing model SQL file
2. Check for common issues:
   - Missing commas
   - Unclosed brackets
   - Invalid Jinja syntax
   - Reserved word conflicts

**For DATA_QUALITY errors:**
1. Read the test definition in schema.yml
2. Query the data to find failing rows:
   ```sql
   SELECT * FROM <model> WHERE <test_condition_fails>;
   ```

**For MISSING_REF errors:**
1. Check if referenced model exists
2. Verify model name spelling
3. Check for circular dependencies

### Step 4: Generate Fix Proposal

Create a structured fix proposal:

```yaml
diagnosis:
  error_type: SCHEMA
  model: stg_orders
  message: "column 'order_date' not found"
  root_cause: "Source column was renamed from 'order_date' to 'ordered_at'"

proposal:
  id: 1
  confidence: 0.85  # 0.0 to 1.0
  description: "Rename column reference in stg_orders.sql"

  changes:
    - file: dbt/models/staging/stg_orders.sql
      action: replace
      old_text: "order_date"
      new_text: "ordered_at"

  verification:
    - "Run: dbt compile --select stg_orders"
    - "Run: dbt run --select stg_orders"
```

### Step 5: Report to User

Present the diagnosis clearly:

```
DIAGNOSIS REPORT
================

Error Type: SCHEMA
Model: stg_orders
Error: column 'order_date' not found

Root Cause Analysis:
  The source data column was renamed from 'order_date' to 'ordered_at'.
  The model SQL still references the old column name.

Proposed Fix (Confidence: 85%):
  File: dbt/models/staging/stg_orders.sql
  Change: Replace 'order_date' with 'ordered_at'

  - cast(order_date as date) as order_date,
  + cast(ordered_at as date) as order_date,

Next Steps:
  1. Run /apply-fix to apply this change
  2. Or manually edit the file
  3. Then run /run-pipeline to retry
```

## Example Usage

```
/diagnose
```
Analyzes the most recent pipeline error.

```
/diagnose "column 'order_date' not found"
```
Diagnoses a specific error message.

```
/diagnose stg_orders
```
Diagnoses issues with a specific model.

## Common Error Patterns and Fixes

### 1. Column Not Found
```
Error: column "X" not found
Fix: Check source schema, update column reference
Confidence: High if column exists with similar name
```

### 2. Relation Does Not Exist
```
Error: relation "X" does not exist
Fix: Check ref() spelling, ensure model exists
Confidence: High if typo detected
```

### 3. Type Mismatch
```
Error: cannot cast type X to Y
Fix: Add explicit cast or fix source data
Confidence: Medium - may require data investigation
```

### 4. Test Failure
```
Error: Test 'unique' failed
Fix: Investigate duplicate data, add deduplication
Confidence: Medium - depends on data source
```

### 5. Jinja Syntax Error
```
Error: unexpected '}'
Fix: Check Jinja block matching
Confidence: High if syntax issue is clear
```

## Output Files

After diagnosis, writes to:
- `logs/errors.log` - Detailed error analysis
- Console output - User-friendly diagnosis report

## Integration

This skill is typically called:
1. After `/run-pipeline` fails
2. By the `pipeline-orchestrator` agent automatically
3. By user when investigating issues
