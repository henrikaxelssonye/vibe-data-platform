# Plan: Azure Storage & GitHub Actions Scheduling

> **Status**: Implemented
> **Created**: 2026-01-13
> **Completed**: 2026-01-13
> **Plan ID**: 002

## Summary

Added cloud-native capabilities to the Vibe Data Platform by integrating Azure Blob Storage for persistent data storage and GitHub Actions for scheduled pipeline execution. Uses Azure CLI scripts for infrastructure provisioning, DuckDB's httpfs extension for direct blob access, and triple notification system (GitHub Issues, Email, Teams/Slack).

## Goals

- [x] Provision Azure Storage Account with raw/duckdb/logs containers
- [x] Create Service Principal for GitHub Actions authentication
- [x] Configure DuckDB httpfs extension to read from Azure Blob URLs
- [x] Create GitHub Actions workflow for scheduled pipeline execution
- [x] Implement notifications: GitHub Issues, Email (Logic App), Webhook
- [x] Migrate existing data to Azure Blob Storage (scripts created)
- [x] Maintain backward compatibility with local development

## Non-Goals

- Terraform or Bicep IaC (user specified Azure CLI only)
- Real-time streaming ingestion
- Multi-region replication

## Architecture

```
                        Azure Storage Account
                    ┌─────────────────────────────┐
                    │  ┌─────┐ ┌──────┐ ┌─────┐  │
                    │  │ raw │ │duckdb│ │logs │  │
                    │  └──▲──┘ └──▲───┘ └──▲──┘  │
                    └─────┼──────┼────────┼─────┘
                          │      │        │
GitHub Actions ───────────┴──────┴────────┴───────
  │
  ├─ Download DuckDB
  ├─ httpfs reads from Azure blob URLs
  ├─ dbt build
  ├─ Upload DuckDB
  └─ On failure → Issues + Email + Webhook
```

## Implementation Phases

### Phase 1: Azure Infrastructure

**Goal**: Provision Azure resources via CLI scripts

1. Created `azure/setup.sh` - provision Storage Account + containers + Service Principal
2. Created `azure/teardown.sh` - cleanup script
3. Created `azure/setup-logic-app.sh` - email notification Logic App
4. Created `azure/credentials.template.env` - template for secrets

**Verification**: Run `az storage container list` after setup

### Phase 2: Data Migration

**Goal**: Upload existing data to Azure and update ingestion scripts

1. Created `scripts/upload_to_azure.py` - upload local data to Azure
2. Created `scripts/sync_azure.py` - bidirectional sync
3. Modified `scripts/ingest_files.py` - added `--azure` flag
4. Updated `config/sources.yml` - added Azure configuration section

**Verification**: Files visible in Azure Portal under raw container

### Phase 3: DuckDB httpfs Configuration

**Goal**: Configure DuckDB to read directly from Azure blob URLs

1. Updated `dbt/profiles.yml` - added `azure` target with httpfs extension
2. Created `dbt/macros/azure_httpfs.sql` - macro to configure Azure auth

**Verification**: `dbt run --target azure` reads from Azure URLs

### Phase 4: GitHub Actions Workflow

**Goal**: Scheduled pipeline execution with cloud persistence

1. Created `.github/workflows/pipeline.yml`:
   - Cron schedule (daily at 6 AM UTC default)
   - Download DuckDB from Azure
   - Run dbt pipeline with `--target azure`
   - Upload DuckDB back to Azure
   - Upload logs
2. Created `config/github_actions.yml` - schedule configuration

**Verification**: Manual workflow trigger completes successfully

### Phase 5: Notifications

**Goal**: Triple notification on failures

1. GitHub Issues - auto-create with labels (in workflow)
2. Email via Logic App - HTTP trigger to send email
3. Teams/Slack webhook - POST to configured URL
4. Created `config/notifications.yml` - channel configuration

**Verification**: Intentional failure triggers all three channels

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `azure/setup.sh` | Create | Provision Azure resources |
| `azure/teardown.sh` | Create | Cleanup resources |
| `azure/setup-logic-app.sh` | Create | Deploy email Logic App |
| `azure/credentials.template.env` | Create | Secrets template |
| `.github/workflows/pipeline.yml` | Create | Scheduled workflow |
| `scripts/upload_to_azure.py` | Create | Upload to Azure |
| `scripts/sync_azure.py` | Create | Bidirectional sync |
| `scripts/ingest_files.py` | Modify | Add `--azure` flag |
| `config/sources.yml` | Modify | Add Azure section |
| `config/notifications.yml` | Create | Notification config |
| `config/github_actions.yml` | Create | Schedule config |
| `dbt/profiles.yml` | Modify | Add azure target |
| `dbt/macros/azure_httpfs.sql` | Create | Azure auth macro |
| `CLAUDE.md` | Modify | Add Azure documentation |

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AZURE_STORAGE_ACCOUNT` | Storage account name |
| `AZURE_STORAGE_KEY` | Storage account access key |
| `AZURE_CREDENTIALS` | Service Principal JSON |
| `LOGIC_APP_EMAIL_URL` | Logic App HTTP trigger URL |
| `NOTIFICATION_WEBHOOK_URL` | Teams/Slack webhook URL |

## Dependencies

- Azure CLI (`az`) installed and authenticated
- Python: `azure-storage-blob`, `azure-identity`
- dbt-duckdb (already installed)

## Verification

```bash
# Phase 1
az storage container list --account-name $AZURE_STORAGE_ACCOUNT

# Phase 2
az storage blob list --container-name raw --account-name $AZURE_STORAGE_ACCOUNT

# Phase 3
cd dbt && dbt run --target azure --select stg_customers

# Phase 4
gh workflow run pipeline.yml

# Phase 5
gh issue list --label pipeline-failure
```

## Rollback Plan

1. Set `storage_mode: local` in `config/sources.yml`
2. Use `target: dev` in dbt (not `azure`)
3. Disable workflow in GitHub Actions settings
4. Run `./azure/teardown.sh` to remove Azure resources

---

## Implementation Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-13 | Phase 1 | Azure CLI scripts created |
| 2026-01-13 | Phase 2 | Data migration scripts created |
| 2026-01-13 | Phase 3 | DuckDB httpfs macro created |
| 2026-01-13 | Phase 4 | GitHub Actions workflow created |
| 2026-01-13 | Phase 5 | Notification config created |
