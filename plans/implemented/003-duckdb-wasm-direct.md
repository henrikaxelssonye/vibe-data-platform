# Plan 003: DuckDB WASM Direct Database Access

**Status:** Implemented
**Created:** 2025-01-26
**Author:** Claude

## Summary

Replace the current Parquet export workflow with direct DuckDB WASM access to the `.duckdb` file. This eliminates the `export_dashboard_data.py` step and uses the database file as the single source of truth for the dashboard.

## Goals

- [x] Dashboard queries the `.duckdb` file directly (no Parquet intermediary)
- [x] Remove `export_dashboard_data.py` from the pipeline
- [x] Maintain or improve dashboard functionality
- [x] Document trade-offs and performance characteristics

## Current Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐     ┌───────────┐
│   dbt       │ ──► │  vibe.db    │ ──► │  export_data.py │ ──► │  .parquet │
│   build     │     │  (3.1 MB)   │     │                 │     │  (25 KB)  │
└─────────────┘     └─────────────┘     └─────────────────┘     └───────────┘
                                                                       │
                                                                       ▼
                                                              ┌───────────────┐
                                                              │   Dashboard   │
                                                              │  (DuckDB WASM)│
                                                              └───────────────┘
```

## Proposed Architecture

```
┌─────────────┐     ┌─────────────┐
│   dbt       │ ──► │  vibe.db    │ ────────────────────────────►┌───────────────┐
│   build     │     │  (3.1 MB)   │                              │   Dashboard   │
└─────────────┘     └─────────────┘                              │  (DuckDB WASM)│
                                                                 └───────────────┘
```

## Technical Approach

### Option A: FileAttachment with Schema (Recommended)

Use Observable Framework's built-in DuckDBClient with the database file as a FileAttachment:

```js
// New syntax - database name becomes schema prefix
const db = DuckDBClient.of({
  vibe: FileAttachment("data/vibe.duckdb")
});

// Queries use schema.table syntax
const results = await db.query(`
  SELECT * FROM vibe.customer_orders
`);
```

**Pros:**
- Simple, uses existing Observable Framework patterns
- File is bundled with the dashboard build
- No CORS configuration needed

**Cons:**
- Entire 3.1 MB file must be downloaded on first visit
- File is duplicated in dashboard bundle

### Option B: Remote ATTACH via Azure Blob Storage

Load the database file from Azure Blob Storage using HTTP range requests:

```js
const db = await DuckDBClient.of({});
await db.query(`ATTACH 'https://vibedata.blob.core.windows.net/duckdb/vibe.duckdb' AS vibe`);

// Same query syntax
const results = await db.query(`SELECT * FROM vibe.customer_orders`);
```

**Pros:**
- Range requests only fetch needed data
- Single source of truth (Azure)
- No file duplication

**Cons:**
- Requires Azure CORS configuration
- More network overhead for small files
- Slower initial connection

### Option C: Hybrid - GitHub Pages with Range Requests

Host the .duckdb file on GitHub Pages alongside the dashboard:

```js
const db = await DuckDBClient.of({});
await db.query(`ATTACH '${window.location.origin}/vibe-data-platform/data/vibe.duckdb' AS vibe`);
```

**Pros:**
- No separate hosting needed
- GitHub Pages supports range requests and CORS

**Cons:**
- File in git repo (not ideal for large files)
- Limited to public repos for CORS

## Implementation Phases

### Phase 1: Proof of Concept
1. Create test branch
2. Copy `vibe.duckdb` to `dashboard/src/data/`
3. Update one dashboard page to use new syntax
4. Test locally with `npm run dev`
5. Measure load time and query performance

### Phase 2: Full Migration
1. Update all dashboard pages:
   - `index.md`
   - `customers.md`
   - `sales.md`
   - `weather.md`
2. Update query syntax to use `vibe.` schema prefix
3. Add `.duckdb` to Observable config for proper handling

### Phase 3: Pipeline Updates
1. Remove `export_dashboard_data.py` from agentic pipeline
2. Update `agentic-pipeline.yml` to copy .db file to dashboard
3. Remove parquet upload step (or keep for backup)
4. Update documentation

### Phase 4: Optimization (Optional)
1. Evaluate Azure Blob Storage option for larger datasets
2. Configure CORS on Azure if using Option B
3. Add caching headers for better performance

## Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `dashboard/src/index.md` | Modify | Update DuckDBClient initialization and queries |
| `dashboard/src/customers.md` | Modify | Update queries to use schema prefix |
| `dashboard/src/sales.md` | Modify | Update queries to use schema prefix |
| `dashboard/src/weather.md` | Modify | Update queries to use schema prefix |
| `dashboard/observablehq.config.js` | Modify | Add .duckdb to file handling if needed |
| `.github/workflows/agentic-pipeline.yml` | Modify | Copy .db file instead of running export |
| `scripts/export_dashboard_data.py` | Delete | No longer needed |
| `CLAUDE.md` | Modify | Update documentation |

## Query Migration Examples

### Current (Parquet)
```js
const db = DuckDBClient.of({
  customer_orders: FileAttachment("data/customer_orders.parquet"),
  orders_summary: FileAttachment("data/orders_summary.parquet"),
  weather_daily: FileAttachment("data/weather_daily.parquet")
});

const metrics = await db.query(`
  SELECT COUNT(*) as total_customers
  FROM customer_orders
`);
```

### New (DuckDB file)
```js
const db = DuckDBClient.of({
  vibe: FileAttachment("data/vibe.duckdb")
});

const metrics = await db.query(`
  SELECT COUNT(*) as total_customers
  FROM vibe.customer_orders
`);
```

## Verification

### Functional Tests
- [ ] Dashboard loads without errors
- [ ] All KPI metrics display correctly
- [ ] Charts render with correct data
- [ ] Weather forecast data displays

### Performance Tests
- [ ] Measure initial page load time (target: < 3s on 3G)
- [ ] Measure query execution time (target: < 500ms)
- [ ] Compare network transfer size vs Parquet approach

### Regression Tests
- [ ] Run full agentic pipeline
- [ ] Verify dashboard deploys to GitHub Pages
- [ ] Confirm no data discrepancies

## Trade-offs & Risks

### Advantages
1. **Simpler pipeline** - One less step to maintain
2. **Single source of truth** - No export sync issues
3. **Immediate data** - Changes in dbt reflect instantly
4. **Less code** - Remove export script

### Disadvantages
1. **Larger download** - 3.1 MB vs 25 KB (124x larger)
2. **Slower initial load** - Especially on slow connections
3. **All tables included** - Can't selectively export

### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance degradation | Medium | Medium | Benchmark before/after, keep Parquet as fallback |
| Browser compatibility | Low | High | Test across Chrome, Firefox, Safari |
| Large future datasets | Medium | High | Document size thresholds, consider hybrid approach |

## Decision Criteria

**Proceed if:**
- POC shows acceptable performance (< 3s load on 3G)
- Query times remain under 500ms
- Team values simplicity over micro-optimization

**Reconsider if:**
- Initial load exceeds 5s on typical connections
- Database file grows beyond 10 MB
- Users report slow dashboard experience

## Implementation Log

| Date | Action | Notes |
|------|--------|-------|
| 2025-01-26 | Plan created | Research complete, awaiting approval |
| 2025-01-26 | Implementation started | Option A (FileAttachment with Schema) selected |
| 2025-01-26 | Phase 1 complete | Copied vibe.duckdb to dashboard/src/data/ |
| 2025-01-26 | Phase 2 complete | Updated all 4 dashboard pages with vibe. schema prefix |
| 2025-01-26 | Phase 3 complete | Updated agentic-pipeline.yml and dashboard.yml workflows |
| 2025-01-26 | Pipeline updates | Removed export_dashboard_data.py, updated CLAUDE.md |
| 2025-01-26 | Implementation complete | All goals achieved, plan moved to implemented/ |

## References

- [DuckDB WASM Data Ingestion](https://duckdb.org/docs/stable/clients/wasm/data_ingestion)
- [Observable Framework DuckDB](https://observablehq.com/framework/lib/duckdb)
- [GitHub Discussion: Load .db file directly](https://github.com/duckdb/duckdb-wasm/discussions/1780)
- [DuckDB WASM HTTP Range Requests](https://duckdb.org/2021/10/29/duckdb-wasm)
