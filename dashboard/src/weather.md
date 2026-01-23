---
title: Weather Insights
---

# Weather Insights

Weather forecast data from Open-Meteo API for Stockholm, Sweden.

```js
import * as Plot from "npm:@observablehq/plot";
import {DuckDBClient} from "npm:@observablehq/duckdb";
```

```js
const db = DuckDBClient.of({
  weather_daily: FileAttachment("data/weather_daily.parquet")
});
```

## Current Conditions

```js
const weather = await db.query(`
  SELECT * FROM weather_daily
  ORDER BY forecast_date
`);

const today = weather[0];
const forecast = weather;
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Temperature</h2>
    <span class="big">${today?.temperature_avg?.toFixed(1) ?? "—"}°C</span>
    <small>${today?.temperature_category ?? ""}</small>
  </div>
  <div class="card">
    <h2>Precipitation</h2>
    <span class="big">${today?.precipitation_mm?.toFixed(1) ?? "—"} mm</span>
    <small>${today?.precipitation_category ?? ""}</small>
  </div>
  <div class="card">
    <h2>Wind Speed</h2>
    <span class="big">${today?.wind_speed_avg?.toFixed(1) ?? "—"} km/h</span>
    <small>${today?.wind_category ?? ""}</small>
  </div>
  <div class="card">
    <h2>Comfort Score</h2>
    <span class="big">${today?.weather_comfort_score?.toFixed(0) ?? "—"}</span>
    <small>out of 100</small>
  </div>
</div>

## 7-Day Temperature Forecast

```js
Plot.plot({
  title: "Temperature Range (°C)",
  width: 800,
  height: 300,
  x: {type: "utc", label: "Date", grid: true},
  y: {label: "Temperature (°C)", grid: true},
  marks: [
    // Temperature range area
    Plot.areaY(forecast, {
      x: "forecast_date",
      y1: "temperature_min",
      y2: "temperature_max",
      fill: "#ff990033",
      curve: "catmull-rom"
    }),
    // Average temperature line
    Plot.lineY(forecast, {
      x: "forecast_date",
      y: "temperature_avg",
      stroke: "#ff9900",
      strokeWidth: 3,
      curve: "catmull-rom"
    }),
    // Data points
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "temperature_avg",
      fill: "#ff9900",
      r: 5,
      tip: {
        format: {
          x: d => d.toLocaleDateString(),
          y: d => `${d.toFixed(1)}°C`
        }
      }
    }),
    // Min/max indicators
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "temperature_min",
      fill: "#0066cc",
      r: 3
    }),
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "temperature_max",
      fill: "#cc0000",
      r: 3
    })
  ]
})
```

<div class="tip">

**Legend:** <span style="color: #cc0000;">●</span> Max Temperature | <span style="color: #ff9900;">●</span> Average | <span style="color: #0066cc;">●</span> Min Temperature

</div>

## Precipitation Forecast

```js
Plot.plot({
  title: "Daily Precipitation (mm)",
  width: 800,
  height: 250,
  x: {type: "utc", label: "Date"},
  y: {label: "Precipitation (mm)", grid: true},
  marks: [
    Plot.barY(forecast, {
      x: "forecast_date",
      y: "precipitation_mm",
      fill: d => d.precipitation_mm > 5 ? "#1e40af" : d.precipitation_mm > 0 ? "#3b82f6" : "#93c5fd",
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

## Weather Comfort Score

The comfort score combines temperature, precipitation, and wind speed into a single metric (0-100).

```js
Plot.plot({
  title: "Daily Comfort Score",
  width: 800,
  height: 250,
  x: {type: "utc", label: "Date"},
  y: {label: "Comfort Score", domain: [0, 100], grid: true},
  marks: [
    // Comfort zones
    Plot.ruleY([30], {stroke: "#ef4444", strokeDasharray: "4,4"}),
    Plot.ruleY([70], {stroke: "#22c55e", strokeDasharray: "4,4"}),
    // Score line
    Plot.lineY(forecast, {
      x: "forecast_date",
      y: "weather_comfort_score",
      stroke: "#8b5cf6",
      strokeWidth: 3,
      curve: "catmull-rom"
    }),
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "weather_comfort_score",
      fill: d => d.weather_comfort_score >= 70 ? "#22c55e" : d.weather_comfort_score >= 30 ? "#f59e0b" : "#ef4444",
      r: 8,
      tip: true
    })
  ]
})
```

<div class="note">

**Comfort Zones:** <span style="color: #22c55e;">●</span> Good (70+) | <span style="color: #f59e0b;">●</span> Moderate (30-70) | <span style="color: #ef4444;">●</span> Poor (<30)

</div>

## Wind Speed

```js
Plot.plot({
  title: "Wind Speed (km/h)",
  width: 800,
  height: 250,
  x: {type: "utc", label: "Date"},
  y: {label: "Wind Speed (km/h)", grid: true},
  marks: [
    Plot.areaY(forecast, {
      x: "forecast_date",
      y: "wind_speed_avg",
      fill: "#06b6d4",
      fillOpacity: 0.3,
      curve: "catmull-rom"
    }),
    Plot.lineY(forecast, {
      x: "forecast_date",
      y: "wind_speed_avg",
      stroke: "#06b6d4",
      strokeWidth: 2,
      curve: "catmull-rom"
    }),
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "wind_speed_avg",
      fill: "#06b6d4",
      tip: true
    })
  ]
})
```

## Detailed Forecast

```js
const forecastTable = forecast.map(d => ({
  date: d.forecast_date,
  day_of_week: d.day_of_week,
  is_weekend: d.is_weekend,
  temp_min: d.temperature_min,
  temp_avg: d.temperature_avg,
  temp_max: d.temperature_max,
  temp_category: d.temperature_category,
  precipitation: d.precipitation_mm,
  precip_category: d.precipitation_category,
  wind: d.wind_speed_avg,
  wind_category: d.wind_category,
  comfort: d.weather_comfort_score
}));
```

```js
Inputs.table(forecastTable, {
  columns: [
    "date",
    "day_of_week",
    "is_weekend",
    "temp_avg",
    "temp_category",
    "precipitation",
    "precip_category",
    "wind",
    "comfort"
  ],
  header: {
    date: "Date",
    day_of_week: "Day",
    is_weekend: "Weekend",
    temp_avg: "Temp (°C)",
    temp_category: "Temp Type",
    precipitation: "Rain (mm)",
    precip_category: "Rain Type",
    wind: "Wind (km/h)",
    comfort: "Comfort"
  },
  format: {
    date: d => d?.toLocaleDateString() ?? "—",
    temp_avg: d => d?.toFixed(1) ?? "—",
    precipitation: d => d?.toFixed(1) ?? "—",
    wind: d => d?.toFixed(1) ?? "—",
    comfort: d => d?.toFixed(0) ?? "—",
    is_weekend: d => d ? "Yes" : "No"
  }
})
```

---

<div class="tip">

**Data Source:** [Open-Meteo API](https://open-meteo.com/) - Free weather forecast data for Stockholm (59.33°N, 18.07°E).

</div>

<style>
.big {
  font-size: 2rem;
  font-weight: bold;
  color: var(--theme-foreground-focus);
}

.card {
  padding: 1.5rem;
  background: var(--theme-background-alt);
  border-radius: 8px;
}

.card h2 {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--theme-foreground-muted);
  margin: 0 0 0.5rem 0;
}

.card small {
  display: block;
  margin-top: 0.25rem;
  color: var(--theme-foreground-muted);
}

.grid {
  display: grid;
  gap: 1rem;
  margin: 1.5rem 0;
}

.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
