# Plan: Weather API Integration (Open-Meteo)

> **Status**: Implemented
> **Created**: 2026-01-22
> **Completed**: 2026-01-22
> **Plan ID**: 003

## Summary

Add weather data ingestion from the Open-Meteo API to enable weather-based analytics. Open-Meteo provides free, no-authentication-required weather forecasts and historical data. This data can be joined with orders to analyze weather impacts on sales patterns, or used standalone for weather trend analysis.

## Research Summary

### API Options Evaluated

| API | Auth Required | Data Type | Recommendation |
|-----|---------------|-----------|----------------|
| **Open-Meteo** | None | Weather forecasts, historical | **Primary choice** |
| REST Countries | None | Country demographics | Good for geo-analysis |
| Exchange Rate API | None | Currency rates | Good for financial data |
| CoinGecko | None | Cryptocurrency | Interesting time-series |

### Why Open-Meteo?

- **No API key required** - Zero setup friction
- **Rich data** - Temperature, precipitation, wind, humidity, UV index, etc.
- **Multiple endpoints** - Forecasts (7-16 days), historical, hourly/daily
- **Well-documented** - URL builder in docs, clear JSON response format
- **Free tier generous** - No rate limits for reasonable usage
- **Global coverage** - Works for any lat/long coordinates

Sources:
- [Open-Meteo Documentation](https://open-meteo.com/en/docs)
- [Big List of Free APIs](https://mixedanalytics.com/blog/list-actually-free-open-no-auth-needed-apis/)
- [Free Public APIs Guide](https://apipheny.io/free-api/)

## Goals

- [x] Configure Open-Meteo API in sources.yml
- [x] Extract weather forecast data for configurable locations
- [x] Create dbt staging model for weather data
- [x] Create mart model joining weather with orders (optional analytics)
- [x] Document the new data source

## Non-Goals

- Historical weather backfill (can be added later)
- Real-time weather streaming
- Multiple location management UI
- Weather-based alerting

## Architecture

### Overview

Weather data will flow through the existing API extraction pipeline, with a new staging model to parse the nested JSON response format.

```
Open-Meteo API
      │
      ▼
┌─────────────────┐
│ extract_api.py  │  ← Fetch weather JSON
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ data/raw/       │  ← api_weather_forecast.json
│ weather_*.json  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ sources.yml     │  ← Register as dbt source
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ stg_weather     │  ← Flatten hourly/daily arrays
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ weather_daily   │  ← Daily weather summary mart
└─────────────────┘
```

### Components

| Component | Purpose |
|-----------|---------|
| `config/sources.yml` | API endpoint configuration |
| `data/raw/api_weather_*.json` | Raw API response storage |
| `dbt/models/sources.yml` | Source table registration |
| `dbt/models/staging/stg_weather_forecast.sql` | Parse and flatten weather data |
| `dbt/models/marts/weather_daily.sql` | Daily weather summary |

### API Response Structure

```json
{
  "latitude": 59.33,
  "longitude": 18.07,
  "timezone": "Europe/Stockholm",
  "hourly": {
    "time": ["2026-01-22T00:00", ...],
    "temperature_2m": [2.1, 1.8, ...],
    "precipitation": [0.0, 0.1, ...]
  },
  "daily": {
    "time": ["2026-01-22", ...],
    "temperature_2m_max": [4.5, ...],
    "temperature_2m_min": [-1.2, ...],
    "precipitation_sum": [2.3, ...]
  }
}
```

## Implementation Phases

### Phase 1: API Configuration

**Goal**: Configure Open-Meteo endpoint and test extraction

1. Add Open-Meteo to `config/sources.yml` with Stockholm coordinates
2. Configure desired weather variables (temp, precipitation, wind, etc.)
3. Test extraction with `python scripts/extract_api.py --api open_meteo`
4. Verify JSON output in `data/raw/`

**Verification**:
```bash
python scripts/extract_api.py --api open_meteo
cat data/raw/api_weather_forecast.json | head -50
```

### Phase 2: dbt Source & Staging

**Goal**: Create dbt models to transform weather data

1. Add `raw_api_weather_forecast` to `dbt/models/sources.yml`
2. Create `stg_weather_forecast.sql` to flatten nested JSON
3. Handle hourly data unnesting (DuckDB `UNNEST` function)
4. Add data quality tests (not null, valid ranges)

**Verification**:
```bash
cd dbt && dbt build --select stg_weather_forecast
dbt show --select stg_weather_forecast --limit 10
```

### Phase 3: Weather Mart

**Goal**: Create usable weather analytics table

1. Create `weather_daily.sql` mart with daily aggregations
2. Add useful calculated fields (feels-like temp, weather category)
3. Add schema tests for data quality

**Verification**:
```bash
cd dbt && dbt build --select weather_daily
dbt test --select weather_daily
```

### Phase 4: Documentation & Testing

**Goal**: Document and integrate with pipeline

1. Update CLAUDE.md with new data source
2. Add weather to full pipeline test
3. Optional: Create weather_orders mart joining weather with sales

**Verification**:
```bash
cd dbt && dbt build
dbt docs generate
```

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `config/sources.yml` | Modify | Add Open-Meteo API configuration |
| `dbt/models/sources.yml` | Modify | Register weather source table |
| `dbt/models/staging/stg_weather_forecast.sql` | Create | Flatten weather JSON |
| `dbt/models/staging/stg_weather_forecast.yml` | Create | Schema tests |
| `dbt/models/marts/weather_daily.sql` | Create | Daily weather mart |
| `dbt/models/marts/weather_daily.yml` | Create | Schema tests |
| `CLAUDE.md` | Modify | Document new source |

## Dependencies

- No new Python dependencies (uses existing `requests` library)
- DuckDB JSON functions (already available)

## Configuration

New API configuration in `config/sources.yml`:

```yaml
sources:
  apis:
    open_meteo:
      enabled: true
      base_url: "https://api.open-meteo.com"
      auth_type: none
      endpoints:
        - name: weather_forecast
          path: /v1/forecast
          method: GET
          params:
            latitude: 59.33    # Stockholm (configurable)
            longitude: 18.07
            hourly: temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m
            daily: temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max
            timezone: auto
            forecast_days: 7
          output_file: data/raw/api_weather_forecast.json
```

## Verification

### Automated Tests

```bash
# Extract weather data
python scripts/extract_api.py --api open_meteo

# Build and test dbt models
cd dbt && dbt build --select +weather_daily
dbt test --select stg_weather_forecast weather_daily

# Show sample data
dbt show --select weather_daily --limit 5
```

### Manual Verification

1. Check `data/raw/api_weather_forecast.json` has valid weather data
2. Run `dbt show --select stg_weather_forecast` - verify columns populated
3. Run `dbt show --select weather_daily` - verify daily aggregations
4. Check for reasonable values (temp -50 to +50°C, precipitation >= 0)

## Rollback Plan

If the feature causes issues:

1. Set `enabled: false` for `open_meteo` in `config/sources.yml`
2. Remove staging/mart models (or leave dormant)
3. Pipeline will skip weather extraction

## Future Enhancements

- Historical weather data endpoint (backfill capability)
- Multiple location support (customer cities)
- Weather-orders correlation analysis mart
- Air quality data integration (Open-Meteo has this endpoint)
- Weather-based anomaly detection

---

## Implementation Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-22 | Research | Evaluated API options, selected Open-Meteo |
| 2026-01-22 | Phase 1 | Added Open-Meteo API config, updated extract_api.py to support query params |
| 2026-01-22 | Phase 2 | Created stg_weather_forecast staging model with schema tests |
| 2026-01-22 | Phase 3 | Created weather_daily mart with comfort score and categorizations |
| 2026-01-22 | Phase 4 | Updated CLAUDE.md documentation, all 22 tests passing |
