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

## Working Directory

**IMPORTANT:** Always run Python scripts from the repository root directory, not from subdirectories.

After running `cd dbt && dbt build`, return to root before running other commands:
```bash
# WRONG - will fail because scripts/export_dashboard_data.py path is relative to root
cd dbt && dbt build
python scripts/export_dashboard_data.py  # Fails! Still in dbt/ directory

# CORRECT - return to root first
cd dbt && dbt build && cd ..
python scripts/export_dashboard_data.py  # Works!

# OR use subshell to avoid directory change
(cd dbt && dbt build)
python scripts/export_dashboard_data.py  # Works! Never left root
```

**Lesson learned (2026-01-23):** The `cd dbt && dbt build` command changes the working directory. Subsequent Python scripts that use relative paths like `scripts/export_dashboard_data.py` will fail with "No such file or directory". Always use subshell `(cd dbt && dbt build)` or return to root with `&& cd ..`.

---

## Common Errors and Fixes

| Error Pattern | Likely Cause | Fix |
|---------------|--------------|-----|
| `column "X" not found` | Typo in column name OR nonexistent column | Check source schema, verify column exists in staging models |
| `relation "X" does not exist` | Missing ref or seed | Run `dbt seed` first |
| `syntax error` | SQL syntax issue | Check for missing commas, parentheses |
| `No such file or directory: scripts/` | Wrong working directory | Return to repo root or use subshell for cd commands |

**Recent fix (2026-01-22):** `orders_summary.sql` referenced `discount_amount` column that didn't exist in `stg_orders`. Fixed by removing discount calculations. Always verify column availability in upstream models before using them.

---

*Last updated: 2026-01-23*
