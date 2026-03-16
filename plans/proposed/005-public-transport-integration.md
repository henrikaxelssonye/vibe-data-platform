# Plan: Public Transport Data Integration (SL Transport API)

> **Status**: Implemented
> **Created**: 2026-02-03
> **Completed**: 2026-02-17
> **Plan ID**: 005

## Summary

Add Stockholm public transport data ingestion from the SL Transport API (via Trafiklab) to enable transit analytics and commute-based insights. The SL Transport API provides free, no-authentication-required access to real-time departures, lines, and stop information for Stockholm's metro, buses, trains, trams, and ferries. This data can be combined with weather data to analyze commute patterns or used standalone for transit analytics.

## Research Summary

### API Options Evaluated

| API | Auth Required | Coverage | Data Type | Recommendation |
|-----|---------------|----------|-----------|----------------|
| **SL Transport API** | None | Stockholm | Real-time departures, lines, stops | **Primary choice** |
| GTFS Sverige 2 | None | All Sweden | Static schedules (GTFS) | Future expansion |
| GTFS Regional | Trafiklab key | Regional | GTFS + real-time | More complex setup |
| SL Realtidsinformation | Trafiklab key | Stockholm | Delays, disruptions | Future enhancement |
| Transitland | Interline key | Global | Aggregated GTFS | Alternative option |

### Why SL Transport API?

- **No API key required** - Zero setup friction (same as Open-Meteo)
- **Real-time data** - Live departure times, not just static schedules
- **Rich coverage** - Metro (tunnelbana), buses, commuter trains, trams, ferries
- **Well-documented** - OpenAPI specs available, clean JSON responses
- **Rate limits reasonable** - Bronze tier allows 10,000 requests/month (free registration optional)
- **Stockholm focus** - Perfect match for the platform's weather data (also Stockholm)

Sources:
- [Trafiklab - SL Transport API](https://www.trafiklab.se/api/sl-transport/)
- [SL Transport API Documentation](https://www.trafiklab.se/api/our-apis/sl/transport/)
- [GTFS Sverige 2 Dataset](https://www.trafiklab.se/api/gtfs-datasets/gtfs-sverige-2/)

## Goals

- [x] Configure SL Transport API in sources.yml (no auth required)
- [x] Extract departure data for configurable stops (e.g., T-Centralen)
- [x] Extract line information for route analytics
- [x] Create dbt staging models for departures and lines
- [x] Create mart model for transit analytics dashboard
- [x] Add transit dashboard page (similar to weather page)
- [x] Document the new data source

## Non-Goals

- Real-time streaming/websocket updates (polling is sufficient)
- Full GTFS schedule database import (can be added later)
- Multi-city support (Stockholm only for MVP)
- Journey planning/routing features
- Disruption/delay tracking (future enhancement)

## Architecture

### Overview

Transport data will flow through the existing API extraction pipeline, with new staging models to parse the nested JSON response format. The pattern mirrors the Open-Meteo weather integration.

```
SL Transport API (Trafiklab)
           │
           ▼
   ┌─────────────────┐
   │ extract_api.py  │  ← Fetch departures & lines JSON
   └────────┬────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ data/raw/               │
   │ ├─ api_sl_departures.json
   │ └─ api_sl_lines.json    │
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ stg_sl_departures.sql   │  ← Parse departures, extract times
   │ stg_sl_lines.sql        │  ← Parse line info
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ transit_departures.sql  │  ← Departure analytics mart
   └─────────────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ dashboard/src/          │
   │ └─ transit.md           │  ← Transit dashboard page
   └─────────────────────────┘
```

### Components

| Component | Purpose |
|-----------|---------|
| `config/sources.yml` | API endpoint configuration for SL Transport |
| `data/raw/api_sl_*.json` | Raw API response storage |
| `dbt/models/sources.yml` | Source table registration |
| `dbt/models/staging/stg_sl_departures.sql` | Parse and flatten departure data |
| `dbt/models/staging/stg_sl_lines.sql` | Parse line information |
| `dbt/models/marts/transit_departures.sql` | Departure analytics mart |
| `dashboard/src/transit.md` | Transit analytics dashboard page |

### API Endpoints

**1. Lines endpoint** - Get all transit lines
```
GET https://transport.integration.sl.se/v1/lines
```

**2. Departures endpoint** - Get real-time departures for a stop
```
GET https://transport.integration.sl.se/v1/sites/{siteId}/departures
```

### API Response Structures

**Lines Response:**
```json
[
  {
    "id": 10,
    "designation": "10",
    "transport_mode": "METRO",
    "group_of_lines": "Tunnelbanans blå linje"
  }
]
```

**Departures Response:**
```json
{
  "departures": [
    {
      "direction": "Kungsträdgården",
      "direction_code": 1,
      "via": null,
      "destination": "Kungsträdgården",
      "state": "EXPECTED",
      "scheduled": "2026-02-03T08:15:00",
      "expected": "2026-02-03T08:16:30",
      "display": "2 min",
      "journey": {
        "id": 12345,
        "state": "NORMALPROGRESS"
      },
      "stop_point": {
        "id": 1051,
        "name": "T-Centralen",
        "designation": "1"
      },
      "line": {
        "id": 10,
        "designation": "10",
        "transport_mode": "METRO",
        "group_of_lines": "Tunnelbanans blå linje"
      }
    }
  ]
}
```

### Key Stop IDs (Stockholm)

| Stop | Site ID | Description |
|------|---------|-------------|
| T-Centralen | 9001 | Central station (all metro lines) |
| Slussen | 9192 | Major hub (metro, buses, ferries) |
| Odenplan | 9117 | Northern hub (metro, commuter rail) |
| Fridhemsplan | 9112 | Western hub (metro lines) |
| Kungsträdgården | 9309 | Blue line terminus |

## Implementation Phases

### Phase 1: API Configuration & Testing

**Goal**: Configure SL Transport endpoints and verify extraction works

1. Add SL Transport API configuration to `config/sources.yml`
   - Lines endpoint (for line metadata)
   - Departures endpoint for T-Centralen (site ID 9001)
2. Test extraction with `python scripts/extract_api.py --api sl_transport`
3. Verify JSON output in `data/raw/`
4. Examine response structure for model design

**Verification**:
```bash
python scripts/extract_api.py --api sl_transport
cat data/raw/api_sl_lines.json | head -50
cat data/raw/api_sl_departures.json | head -100
```

### Phase 2: dbt Staging Models

**Goal**: Create dbt models to transform transit data

1. Add sources to `dbt/models/sources.yml`
2. Create `stg_sl_lines.sql` to parse line information
   - Extract: line_id, designation, transport_mode, group_of_lines
   - Add transport mode categories (METRO, BUS, TRAIN, TRAM, FERRY)
3. Create `stg_sl_departures.sql` to flatten departure data
   - Extract: departure_time, line, destination, stop_point, delay
   - Calculate delay_minutes from scheduled vs expected
4. Create schema test files (`.yml`) for both models

**Verification**:
```bash
cd dbt && dbt build --select stg_sl_lines stg_sl_departures
dbt show --select stg_sl_lines --limit 10
dbt show --select stg_sl_departures --limit 20
```

### Phase 3: Transit Analytics Mart

**Goal**: Create usable transit analytics table

1. Create `transit_departures.sql` mart with analytics fields:
   - Departure counts by transport mode
   - Average delays by line
   - Peak hour classification
   - Weather correlation fields (join with weather_daily)
2. Add useful calculated fields:
   - `is_delayed` boolean (expected > scheduled + 2 min)
   - `delay_category` (on_time, slight_delay, significant_delay)
   - `time_of_day` (morning_rush, midday, evening_rush, night)
3. Add schema tests for data quality

**Verification**:
```bash
cd dbt && dbt build --select transit_departures
dbt test --select transit_departures
dbt show --select transit_departures --limit 10
```

### Phase 4: Dashboard Integration

**Goal**: Add transit page to Observable dashboard

1. Create `dashboard/src/transit.md` page with:
   - Next departures table (real-time view)
   - Departures by transport mode chart
   - Delay statistics
   - Line frequency analysis
2. Update `dashboard/observablehq.config.js` navigation
3. Test dashboard locally

**Verification**:
```bash
# Copy database to dashboard
cp data/processed/vibe.duckdb dashboard/src/data/vibe.duckdb

# Preview dashboard
cd dashboard && npm run dev
# Navigate to /transit page
```

### Phase 5: Documentation & Integration

**Goal**: Document and integrate with full pipeline

1. Update `CLAUDE.md` with new data source and models
2. Add transit extraction to agentic pipeline workflow
3. Test full pipeline: extract → dbt build → dashboard build

**Verification**:
```bash
# Full pipeline test
python scripts/extract_api.py --api open_meteo
python scripts/extract_api.py --api sl_transport
cd dbt && dbt build
cp data/processed/vibe.duckdb dashboard/src/data/vibe.duckdb
cd ../dashboard && npm run build
```

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `config/sources.yml` | Modify | Add SL Transport API configuration |
| `dbt/models/sources.yml` | Modify | Register transit source tables |
| `dbt/models/staging/stg_sl_lines.sql` | Create | Parse line metadata |
| `dbt/models/staging/stg_sl_lines.yml` | Create | Schema tests for lines |
| `dbt/models/staging/stg_sl_departures.sql` | Create | Parse departure data |
| `dbt/models/staging/stg_sl_departures.yml` | Create | Schema tests for departures |
| `dbt/models/marts/transit_departures.sql` | Create | Transit analytics mart |
| `dbt/models/marts/transit_departures.yml` | Create | Schema tests for mart |
| `dashboard/src/transit.md` | Create | Transit dashboard page |
| `dashboard/observablehq.config.js` | Modify | Add transit to navigation |
| `CLAUDE.md` | Modify | Document new source |

## Dependencies

- No new Python dependencies (uses existing `requests` library)
- DuckDB JSON functions (already available)
- Observable Framework (already configured)

## Configuration

New API configuration in `config/sources.yml`:

```yaml
sources:
  apis:
    # SL Transport API (Stockholm public transport - free, no auth)
    sl_transport:
      enabled: true
      base_url: "https://transport.integration.sl.se/v1"
      auth_type: none
      endpoints:
        - name: lines
          path: /lines
          method: GET
          output_file: data/raw/api_sl_lines.json
        - name: departures_tcentralen
          path: /sites/9001/departures
          method: GET
          params:
            forecast: 60  # Minutes ahead to fetch
          output_file: data/raw/api_sl_departures.json
```

## Verification

### Automated Tests

```bash
# Extract transport data
python scripts/extract_api.py --api sl_transport

# Build and test dbt models
cd dbt && dbt build --select +transit_departures
dbt test --select stg_sl_lines stg_sl_departures transit_departures

# Show sample data
dbt show --select stg_sl_lines --limit 5
dbt show --select transit_departures --limit 10

# Build dashboard
cp ../data/processed/vibe.duckdb ../dashboard/src/data/vibe.duckdb
cd ../dashboard && npm run build
```

### Manual Verification

1. Check `data/raw/api_sl_lines.json` has metro, bus, train lines
2. Check `data/raw/api_sl_departures.json` has real-time departures
3. Run `dbt show --select stg_sl_departures` - verify columns populated
4. Run `dbt show --select transit_departures` - verify analytics fields
5. Preview dashboard at localhost - check transit page renders

## Rollback Plan

If the feature causes issues:

1. Set `enabled: false` for `sl_transport` in `config/sources.yml`
2. Comment out transit models in dbt (or delete)
3. Remove transit.md from dashboard
4. Pipeline will skip transport extraction

## Future Enhancements

- **Multiple stops**: Extract departures from multiple key stations
- **GTFS static data**: Import full schedule data for historical analysis
- **Disruption tracking**: Add SL Realtidsinformation API for delays/alerts
- **Weather correlation**: Mart joining transit delays with weather conditions
- **Commute patterns**: If user location data available, analyze commute times
- **Real-time refresh**: More frequent polling for live dashboard updates
- **All-Sweden expansion**: Use GTFS Sverige 2 for national coverage

---

## Planning Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-02-03 | Research | Evaluated API options, selected SL Transport API |
| 2026-02-17 | Implementation | Added SL extraction config, dbt staging/mart models, dashboard transit page, and docs updates |
| 2026-02-17 | Verification | `python scripts/extract_api.py --api sl_transport`, `dbt build --select stg_sl_lines stg_sl_departures transit_departures`, `npm run build` all passed |
