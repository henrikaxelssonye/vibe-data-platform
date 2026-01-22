# Agent Notes

This file contains notes and learnings from the Claude agent's pipeline runs. The agent can read and update this file to avoid repeating mistakes.

---

## GitHub Labels

**Available labels in this repository:**
- `bug` - For bug reports
- `pipeline-failure` - For pipeline failures (NOT `pipeline`)
- `auto-healing` - For issues being auto-fixed (must be created first)
- `needs-triage` - For issues requiring human attention
- `automated` - For automated actions

**Do NOT use these labels (they don't exist):**
- `pipeline` - Use `pipeline-failure` instead
- `auto-healing` - Must create this label first or skip it

**Lesson learned (2026-01-22):** When creating issues, only use labels that exist. The `pipeline` label does not exist - use `pipeline-failure` instead. If a label doesn't exist and isn't critical, omit it rather than failing.

---

## Issue Creation Tips

1. Keep issue titles concise but descriptive
2. Use existing labels only
3. Include the workflow run URL for context
4. Store the issue number for later updates

---

## Common Errors and Fixes

| Error Pattern | Likely Cause | Fix |
|---------------|--------------|-----|
| `column "X" not found` | Typo in column name OR nonexistent column | Check source schema, verify column exists in staging models |
| `relation "X" does not exist` | Missing ref or seed | Run `dbt seed` first |
| `syntax error` | SQL syntax issue | Check for missing commas, parentheses |

**Recent fix (2026-01-22):** `orders_summary.sql` referenced `discount_amount` column that didn't exist in `stg_orders`. Fixed by removing discount calculations. Always verify column availability in upstream models before using them.

---

*Last updated: 2026-01-22*
