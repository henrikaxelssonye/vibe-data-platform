---
name: apply-fix
description: Apply proposed fixes to dbt models with automatic backup. Use after /diagnose to implement suggested changes.
---

# apply-fix

A skill for safely applying fix proposals to dbt models with backup and verification.

## Instructions

When this skill is invoked:

### Step 1: Read Configuration

Load execution mode from `config/execution_mode.yml`:

```yaml
execution:
  mode: human-in-loop  # or "autonomous"
autonomous:
  min_confidence: 0.8
  create_backups: true
```

Check:
- Current mode (autonomous vs human-in-loop)
- Whether backups are enabled
- Minimum confidence for auto-apply

### Step 2: Parse Arguments

| Argument | Description |
|----------|-------------|
| (none) | Apply most recent fix proposal |
| `--file <path>` | Specify file to modify |
| `--old "<text>"` | Text to replace |
| `--new "<text>"` | Replacement text |
| `--auto` | Skip confirmation (autonomous mode) |
| `--dry-run` | Preview changes without applying |
| `--confidence <0-1>` | Confidence score for this fix |

### Step 3: Generate Diff Preview

Read the target file and generate a contextual diff view:

```
PROPOSED CHANGE
===============

File: dbt/models/staging/stg_orders.sql
Confidence: 95%

Context (3 lines before/after):
────────────────────────────────────────
   7 │     select
   8 │         order_id,
   9 │         customer_id,
  10 │ -       cast(purchase_date as date) as order_date,  -- ERROR
  10 │ +       cast(order_date as date) as order_date,
  11 │         product_name,
  12 │         quantity,
  13 │         unit_price,
────────────────────────────────────────

Summary: Replace 'purchase_date' with 'order_date'
```

### Step 4: Mode-Based Confirmation

**Autonomous Mode** (`--auto` or config mode=autonomous):
- If confidence >= min_confidence (default 0.8): Apply automatically
- If confidence < min_confidence: Fall back to human-in-loop
- Log: `[AUTO] Applying fix with confidence X%`

**Human-in-Loop Mode** (default):
```
┌─────────────────────────────────────────┐
│         APPROVAL REQUIRED               │
├─────────────────────────────────────────┤
│ File: stg_orders.sql                    │
│ Line: 10                                │
│ Confidence: 95%                         │
│                                         │
│ - cast(purchase_date as date)           │
│ + cast(order_date as date)              │
│                                         │
│ Backup: stg_orders.sql.bak.20240115...  │
├─────────────────────────────────────────┤
│ Apply this fix? [Y/n/d]                 │
│   Y = Yes, apply                        │
│   n = No, skip                          │
│   d = Show full diff                    │
└─────────────────────────────────────────┘
```

Wait for user response before proceeding.

### Step 5: Create Backup

Before modifying, create timestamped backup:

```bash
cp <file> <file>.bak.$(date +%Y%m%d%H%M%S)
```

Record backup path for potential rollback.

### Step 6: Apply the Fix

Use the Edit tool:
```
Edit file: <path>
old_string: <exact text to find>
new_string: <replacement text>
```

### Step 7: Verify the Fix

Run verification steps:

1. **Syntax Check:**
   ```bash
   cd C:/kund/vibe-data-platform/dbt && dbt compile --select <model>
   ```

2. **If compile fails:** Auto-rollback from backup

3. **Optional full validation:**
   ```bash
   cd C:/kund/vibe-data-platform/dbt && dbt build --select <model>
   ```

### Step 8: Handle Verification Failure

If verification fails:

```
FIX VERIFICATION FAILED
=======================

Applied change caused new error:
  <new error message>

Rolling back...
  Restored: stg_orders.sql from backup

Status: Fix reverted, original error remains.
Suggestion: Review the fix manually or try /diagnose again.
```

### Step 9: Log and Report

**Log to `logs/fixes.log`:**
```
[TIMESTAMP] FIX_APPLIED mode=human-in-loop file=stg_orders.sql confidence=95% status=success
```

**Success Report:**
```
FIX APPLIED SUCCESSFULLY
========================

┌─ Summary ─────────────────────────────┐
│ File:       stg_orders.sql            │
│ Change:     purchase_date → order_date│
│ Confidence: 95%                       │
│ Backup:     stg_orders.sql.bak.*      │
│ Verified:   dbt compile passed        │
└───────────────────────────────────────┘

Next steps:
  • Run /validate to check data quality
  • Run /run-pipeline for full pipeline test
```

## Example Usage

```
/apply-fix
```
Apply most recent fix interactively.

```
/apply-fix --auto
```
Apply fix without confirmation (respects min_confidence).

```
/apply-fix --dry-run
```
Preview the change without applying.

```
/apply-fix --file dbt/models/staging/stg_orders.sql --old "purchase_date" --new "order_date"
```
Apply specific fix to specific file.

## Mode Comparison

| Feature | Human-in-Loop | Autonomous |
|---------|---------------|------------|
| Confirmation | Required | Skipped if confidence >= 80% |
| Backup | Always | Configurable |
| Rollback | Manual | Automatic |
| Logging | Verbose | Verbose |
| Best for | Production | Development/Testing |

## Safety Features

1. **Backup before modify** - Always creates timestamped backup
2. **Syntax verification** - Runs dbt compile after fix
3. **Auto-rollback** - Restores backup if verification fails
4. **Audit trail** - All fixes logged to logs/fixes.log
5. **Confidence gating** - Low confidence fixes require approval
6. **Diff preview** - See exactly what will change

## Integration

Called by:
- User after `/diagnose` output
- `pipeline-orchestrator` agent in self-healing loop
- Any workflow needing safe code modifications

After successful fix:
- Run `/validate` for data quality checks
- Run `/run-pipeline` to test full pipeline
