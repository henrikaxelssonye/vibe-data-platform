# Plan: Dashboard UI with Observable Framework

> **Status**: Implemented
> **Created**: 2025-01-22
> **Completed**: -
> **Plan ID**: 004

## Summary

Add a web-based dashboard UI to the Vibe Data Platform using Observable Framework, a static site generator optimized for data apps. The dashboard will visualize customer analytics, sales performance, and weather data from the existing dbt models. It will be hosted on GitHub Pages for zero-cost, serverless deployment, with data queried directly in the browser using DuckDB-WASM.

## Goals

- [ ] Create an interactive dashboard displaying key business metrics
- [ ] Host the dashboard on GitHub Pages (free, static hosting)
- [ ] Enable client-side data querying with DuckDB-WASM for fast interactions
- [ ] Integrate with existing dbt data exports (Parquet files)
- [ ] Set up automated dashboard builds via GitHub Actions
- [ ] Provide three dashboard views: Customer Analytics, Sales Performance, Weather Insights

## Non-Goals

- Real-time streaming data (batch refresh only)
- User authentication/authorization (public dashboard)
- Data editing capabilities (read-only visualization)
- Complex BI features like scheduled reports or alerting
- Mobile-first design (desktop-focused initially)

## Technology Selection

### Why Observable Framework?

After evaluating alternatives, Observable Framework is recommended:

| Criteria | Observable Framework | Evidence.dev | Custom DuckDB-WASM | Rill |
|----------|---------------------|--------------|-------------------|------|
| GitHub Pages Support | Native | Yes | Yes | No (needs server) |
| DuckDB Integration | Excellent | Good | Manual | Built-in |
| Learning Curve | Low-Medium | Low | High | Low |
| Visualization Library | Observable Plot, D3 | Built-in charts | BYO (Plotly, etc.) | Opinionated |
| dbt Compatibility | Good (Parquet/DuckDB) | Excellent | Good | Good |
| Active Development | Very active | Active | N/A | Active |
| Static Export | Built-in | Built-in | Manual | Not supported |

**Key advantages:**
- Native DuckDB-WASM support with SQL code blocks
- Data loaders precompute snapshots at build time
- Deploys as pure static files to GitHub Pages
- Rich visualization with Observable Plot and D3.js
- Markdown-based pages with reactive JavaScript

### Alternative Considered: Evidence.dev

Evidence.dev is also excellent for dbt-centric workflows with its "BI as code" approach. It could be a future alternative if the team prefers a more SQL-native workflow.

## Architecture

### Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Build Pipeline (GitHub Actions)              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │
│  │  dbt build  │───▶│ Export to   │───▶│ Observable Framework    │  │
│  │  (DuckDB)   │    │ Parquet     │    │ Build (npm run build)   │  │
│  └─────────────┘    └─────────────┘    └───────────┬─────────────┘  │
│                                                     │                │
│                                                     ▼                │
│                                        ┌─────────────────────────┐  │
│                                        │  Deploy to GitHub Pages │  │
│                                        │  (Static HTML/JS/CSS)   │  │
│                                        └─────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                         Browser (End User)                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Observable Dashboard                          ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ ││
│  │  │ Customer    │  │ Sales       │  │ Weather                 │ ││
│  │  │ Analytics   │  │ Performance │  │ Insights                │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ ││
│  │                           │                                      ││
│  │                           ▼                                      ││
│  │               ┌─────────────────────────┐                       ││
│  │               │   DuckDB-WASM Engine    │                       ││
│  │               │   (In-Browser Queries)  │                       ││
│  │               └───────────┬─────────────┘                       ││
│  │                           │                                      ││
│  │                           ▼                                      ││
│  │               ┌─────────────────────────┐                       ││
│  │               │   Parquet Data Files    │                       ││
│  │               │   (Cached in Browser)   │                       ││
│  │               └─────────────────────────┘                       ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Purpose |
|-----------|---------|
| Observable Framework | Static site generator for data dashboards |
| DuckDB-WASM | In-browser SQL engine for client-side queries |
| Observable Plot | Charting library for visualizations |
| GitHub Pages | Free static hosting with CDN |
| GitHub Actions | Automated build and deploy pipeline |
| Parquet Files | Columnar data format for efficient browser loading |

### Data Flow

```
dbt models (DuckDB) → Export to Parquet → GitHub Pages CDN → Browser → DuckDB-WASM → Visualization
```

## Dashboard Pages

### 1. Home / Overview

- KPI cards: Total Customers, Total Revenue, Total Orders, Avg Order Value
- Recent activity summary
- Quick navigation to detailed views

### 2. Customer Analytics

- Customer segment distribution (pie/donut chart)
- Revenue by customer (bar chart)
- Customer geographic distribution (by city)
- Customer lifetime value trends
- Interactive customer table with search/filter

### 3. Sales Performance

- Revenue over time (line chart)
- Order status breakdown (completed/pending/cancelled)
- Product performance comparison
- Top products by revenue
- Product margin analysis

### 4. Weather Insights

- 7-day weather forecast visualization
- Temperature and precipitation trends
- Weather comfort score over time
- Weekend vs weekday comparison
- Potential: Weather correlation with sales (experimental)

## Implementation Phases

### Phase 1: Project Setup

**Goal**: Initialize Observable Framework project and configure GitHub Pages deployment

1. Initialize Observable Framework project in `dashboard/` directory
2. Configure `observablehq.config.js` for project settings
3. Set up basic page structure (index, customers, sales, weather)
4. Create GitHub Actions workflow for automated deployment
5. Configure GitHub Pages to serve from `gh-pages` branch
6. Verify blank dashboard deploys successfully

**Verification**: Empty dashboard accessible at `https://<username>.github.io/vibe-data-platform/`

### Phase 2: Data Export Pipeline

**Goal**: Create automated data export from dbt to Parquet files for dashboard consumption

1. Create `scripts/export_dashboard_data.py` to export dbt models to Parquet
2. Export key tables: `customer_orders`, `orders_summary`, `weather_daily`
3. Add data loader scripts for Observable Framework
4. Configure data loaders to process Parquet files at build time
5. Update GitHub Actions to run export before dashboard build

**Verification**: Parquet files generated and loadable in Observable Framework

### Phase 3: Core Visualizations

**Goal**: Build the main dashboard pages with interactive charts

1. Implement Home page with KPI cards and overview metrics
2. Build Customer Analytics page:
   - Customer segment pie chart
   - Revenue by customer bar chart
   - Customer data table with DuckDB queries
3. Build Sales Performance page:
   - Order trends line chart
   - Product comparison charts
   - Status breakdown visualization
4. Build Weather Insights page:
   - Temperature forecast chart
   - Precipitation visualization
   - Comfort score display

**Verification**: All four pages render with real data and interactive elements

### Phase 4: Interactivity & Polish

**Goal**: Add cross-filtering, improve UX, and finalize styling

1. Add interactive filters (date range, customer segment, product)
2. Implement cross-filtering between charts using Mosaic (optional)
3. Add responsive navigation and consistent styling
4. Optimize Parquet file sizes for faster loading
5. Add loading states and error handling
6. Create dashboard documentation

**Verification**: Dashboard is interactive, styled consistently, and performs well

### Phase 5: CI/CD Integration

**Goal**: Fully automated pipeline from data changes to dashboard updates

1. Update `agentic-pipeline.yml` to trigger dashboard rebuild after dbt success
2. Add dashboard build step to main pipeline workflow
3. Configure caching for faster builds
4. Add dashboard link to pipeline notifications
5. Document manual refresh process

**Verification**: Dashboard auto-updates when dbt pipeline runs successfully

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `dashboard/` | Create | Observable Framework project directory |
| `dashboard/observablehq.config.js` | Create | Framework configuration |
| `dashboard/package.json` | Create | Node.js dependencies |
| `dashboard/src/index.md` | Create | Home/overview page |
| `dashboard/src/customers.md` | Create | Customer analytics page |
| `dashboard/src/sales.md` | Create | Sales performance page |
| `dashboard/src/weather.md` | Create | Weather insights page |
| `dashboard/src/data/` | Create | Data loaders directory |
| `dashboard/src/components/` | Create | Reusable chart components |
| `scripts/export_dashboard_data.py` | Create | Parquet export script |
| `.github/workflows/dashboard.yml` | Create | Dashboard build/deploy workflow |
| `.github/workflows/agentic-pipeline.yml` | Modify | Add dashboard build trigger |
| `CLAUDE.md` | Modify | Document dashboard commands |

## Dependencies

### Dashboard (Node.js)
```bash
npm create @observablehq/framework@latest dashboard
cd dashboard
npm install
```

### Data Export (Python)
```bash
pip install pyarrow pandas duckdb
```

## Configuration

### observablehq.config.js

```javascript
export default {
  title: "Vibe Data Platform",
  pages: [
    {name: "Overview", path: "/"},
    {name: "Customers", path: "/customers"},
    {name: "Sales", path: "/sales"},
    {name: "Weather", path: "/weather"}
  ],
  theme: "default",
  toc: true,
  pager: true,
  footer: "Vibe Data Platform Dashboard"
};
```

### GitHub Pages Configuration

```yaml
# In repository settings
# Pages > Source: Deploy from a branch
# Branch: gh-pages / root
```

## Verification

### Automated Tests

```bash
# Build dashboard locally
cd dashboard && npm run build

# Preview dashboard
cd dashboard && npm run preview

# Export test data
python scripts/export_dashboard_data.py --test
```

### Manual Verification

1. Navigate to GitHub Pages URL
2. Verify all four pages load without errors
3. Confirm charts display real data from dbt models
4. Test interactive filters and cross-filtering
5. Verify mobile responsiveness (basic)
6. Check that data refreshes after pipeline run

## Rollback Plan

If the feature causes issues:

1. Disable GitHub Actions workflow (`dashboard.yml`)
2. Delete `gh-pages` branch to remove published dashboard
3. Dashboard is isolated in `dashboard/` directory - delete to fully remove

## Cost Estimate

| Resource | Cost |
|----------|------|
| GitHub Pages Hosting | Free (public repos) |
| GitHub Actions (build) | Free tier (2,000 min/month) |
| Observable Framework | Free (MIT license) |
| **Total** | **$0/month** |

## Future Enhancements

- Add date range picker for historical analysis
- Implement drill-down from summary to detail views
- Add export to PDF/PNG functionality
- Create embedded dashboard widgets for README
- Add dark mode theme support
- Implement real-time data refresh (websocket connection to API)
- Add user preferences with localStorage
- Consider Evidence.dev as alternative framework

## References

- [Observable Framework Documentation](https://observablehq.com/framework/)
- [DuckDB-WASM](https://duckdb.org/docs/api/wasm/overview)
- [Observable Framework + DuckDB](https://observablehq.observablehq.cloud/framework/lib/duckdb)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Mosaic - UW Interactive Data Lab](https://idl.uw.edu/mosaic/)
- [Evidence.dev](https://github.com/evidence-dev/evidence)

---

## Implementation Log

| Date | Phase | Notes |
|------|-------|-------|
| 2025-01-22 | Planning | Plan created, awaiting approval |
| 2025-01-22 | Phase 1 | Observable Framework project initialized |
| 2025-01-22 | Phase 2 | Data export script created (export_dashboard_data.py) |
| 2025-01-22 | Phase 3 | All 4 dashboard pages built (index, customers, sales, weather) |
| 2025-01-22 | Phase 4 | Interactive filters, charts, and styling added |
| 2025-01-22 | Phase 5 | GitHub Actions workflow created (dashboard.yml) |
| 2025-01-22 | Complete | Dashboard builds successfully, documentation updated |
