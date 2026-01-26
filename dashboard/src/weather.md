---
title: Weather Insights
---

# Weather Insights

Weather forecast data from Open-Meteo API for Stockholm, Sweden.

```js
import * as Plot from "npm:@observablehq/plot";
import {DuckDBClient} from "npm:@observablehq/duckdb";
import * as Inputs from "npm:@observablehq/inputs";

// Dark Horse Analytics color palette
const dhColors = {
  gold: "#c6b356",
  goldDim: "#9d8e45",
  blue: "#60a5fa",
  green: "#4ade80",
  pink: "#f472b6",
  purple: "#a78bfa",
  orange: "#fb923c",
  cyan: "#22d3ee",
  text: "#f1f1ef",
  textMuted: "#a0aab8",
  bgCard: "#2a3a4d",
  border: "#3a4a5d",
  success: "#4ade80",
  warning: "#fbbf24",
  danger: "#f87171"
};
```

```js
// Initialize DuckDB with the database file directly
const db = DuckDBClient.of({
  vibe: FileAttachment("data/vibe.duckdb")
});
```

## Current Conditions

```js
const weatherResult = await db.query(`
  SELECT * FROM vibe.weather_daily
  ORDER BY forecast_date
`);

// Convert DuckDB Arrow result to JS array
const forecast = Array.from(weatherResult);
const today = forecast[0];
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Temperature</h2>
    <span class="big">${today?.temperature_avg_c?.toFixed(1) ?? "—"}°C</span>
    <small>${today?.temperature_category ?? ""}</small>
  </div>
  <div class="card">
    <h2>Precipitation</h2>
    <span class="big">${today?.precipitation_mm?.toFixed(1) ?? "—"} mm</span>
    <small>${today?.precipitation_category ?? ""}</small>
  </div>
  <div class="card">
    <h2>Wind Speed</h2>
    <span class="big">${today?.wind_speed_max_kmh?.toFixed(1) ?? "—"} km/h</span>
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
  width: 800,
  height: 300,
  marginTop: 30,
  marginBottom: 50,
  marginLeft: 50,
  marginRight: 30,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    type: "utc",
    label: "Date",
    labelOffset: 40,
    tickFormat: d => d.toLocaleDateString('en', {weekday: 'short', month: 'short', day: 'numeric'}),
    line: false,
    tickSize: 0
  },
  y: {
    label: "Temperature (°C)",
    labelOffset: 40,
    grid: true,
    line: false,
    tickSize: 0
  },
  marks: [
    // Temperature range area
    Plot.areaY(forecast, {
      x: "forecast_date",
      y1: "temperature_min_c",
      y2: "temperature_max_c",
      fill: dhColors.gold,
      fillOpacity: 0.15,
      curve: "catmull-rom"
    }),
    // Average temperature line
    Plot.lineY(forecast, {
      x: "forecast_date",
      y: "temperature_avg_c",
      stroke: dhColors.gold,
      strokeWidth: 3,
      curve: "catmull-rom"
    }),
    // Data points
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "temperature_avg_c",
      fill: dhColors.gold,
      stroke: dhColors.bgCard,
      strokeWidth: 2,
      r: 6,
      tip: {
        format: {
          x: d => d.toLocaleDateString('en', {weekday: 'long', month: 'long', day: 'numeric'}),
          y: d => d.toFixed(1) + "°C",
          fill: false,
          stroke: false
        }
      }
    }),
    // Min/max indicators
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "temperature_min",
      fill: dhColors.blue,
      stroke: dhColors.bgCard,
      strokeWidth: 1,
      r: 4
    }),
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "temperature_max",
      fill: dhColors.danger,
      stroke: dhColors.bgCard,
      strokeWidth: 1,
      r: 4
    })
  ]
})
```

<div class="tip">

**Legend:** <span style="color: #f87171;">●</span> Max Temperature | <span style="color: #c6b356;">●</span> Average | <span style="color: #60a5fa;">●</span> Min Temperature

</div>

## Precipitation Forecast

```js
Plot.plot({
  width: 800,
  height: 250,
  marginTop: 25,
  marginBottom: 50,
  marginLeft: 50,
  marginRight: 30,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Date",
    labelOffset: 40,
    tickFormat: d => d.toLocaleDateString('en', {weekday: 'short', day: 'numeric'}),
    line: false,
    tickSize: 0
  },
  y: {
    label: "Precipitation (mm)",
    labelOffset: 40,
    grid: true,
    line: false,
    tickSize: 0
  },
  marks: [
    Plot.rectY(forecast, {
      x: "forecast_date",
      y: "precipitation_mm",
      fill: d => d.precipitation_mm > 5 ? dhColors.blue : d.precipitation_mm > 0 ? dhColors.cyan : dhColors.purple,
      rx: 4,
      interval: "day",
      tip: {
        format: {
          x: d => d.toLocaleDateString('en', {weekday: 'long', month: 'short', day: 'numeric'}),
          y: d => d.toFixed(1) + " mm",
          fill: false
        }
      }
    }),
    Plot.text(forecast, {
      x: "forecast_date",
      y: "precipitation_mm",
      text: d => d.precipitation_mm > 0 ? d.precipitation_mm.toFixed(1) : "",
      dy: -12,
      fill: dhColors.textMuted,
      fontSize: 10
    })
  ]
})
```

## Weather Comfort Score

The comfort score combines temperature, precipitation, and wind speed into a single metric (0-100).

```js
Plot.plot({
  width: 800,
  height: 260,
  marginTop: 25,
  marginBottom: 50,
  marginLeft: 50,
  marginRight: 30,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    type: "utc",
    label: "Date",
    labelOffset: 40,
    tickFormat: d => d.toLocaleDateString('en', {weekday: 'short', day: 'numeric'}),
    line: false,
    tickSize: 0
  },
  y: {
    label: "Comfort Score",
    labelOffset: 40,
    domain: [0, 100],
    grid: true,
    line: false,
    tickSize: 0
  },
  marks: [
    // Comfort zone backgrounds
    Plot.rectY([{y1: 0, y2: 30}], {
      y1: "y1",
      y2: "y2",
      fill: dhColors.danger,
      fillOpacity: 0.08
    }),
    Plot.rectY([{y1: 70, y2: 100}], {
      y1: "y1",
      y2: "y2",
      fill: dhColors.success,
      fillOpacity: 0.08
    }),
    // Comfort zone lines
    Plot.ruleY([30], {stroke: dhColors.danger, strokeDasharray: "6,4", strokeOpacity: 0.5}),
    Plot.ruleY([70], {stroke: dhColors.success, strokeDasharray: "6,4", strokeOpacity: 0.5}),
    // Score area
    Plot.areaY(forecast, {
      x: "forecast_date",
      y: "weather_comfort_score",
      fill: dhColors.purple,
      fillOpacity: 0.2,
      curve: "catmull-rom"
    }),
    // Score line
    Plot.lineY(forecast, {
      x: "forecast_date",
      y: "weather_comfort_score",
      stroke: dhColors.purple,
      strokeWidth: 3,
      curve: "catmull-rom"
    }),
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "weather_comfort_score",
      fill: d => d.weather_comfort_score >= 70 ? dhColors.success : d.weather_comfort_score >= 30 ? dhColors.warning : dhColors.danger,
      stroke: dhColors.bgCard,
      strokeWidth: 2,
      r: 8,
      tip: {
        format: {
          x: d => d.toLocaleDateString('en', {weekday: 'long', month: 'short', day: 'numeric'}),
          y: d => d.toFixed(0) + " / 100",
          fill: false,
          stroke: false
        }
      }
    }),
    Plot.text(forecast, {
      x: "forecast_date",
      y: "weather_comfort_score",
      text: d => d.weather_comfort_score.toFixed(0),
      dy: -15,
      fill: dhColors.textMuted,
      fontSize: 10,
      fontWeight: 600
    })
  ]
})
```

<div class="note">

**Comfort Zones:** <span style="color: #4ade80;">●</span> Good (70+) | <span style="color: #fbbf24;">●</span> Moderate (30-70) | <span style="color: #f87171;">●</span> Poor (<30)

</div>

## Wind Speed

```js
Plot.plot({
  width: 800,
  height: 250,
  marginTop: 25,
  marginBottom: 50,
  marginLeft: 50,
  marginRight: 30,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    type: "utc",
    label: "Date",
    labelOffset: 40,
    tickFormat: d => d.toLocaleDateString('en', {weekday: 'short', day: 'numeric'}),
    line: false,
    tickSize: 0
  },
  y: {
    label: "Wind Speed (km/h)",
    labelOffset: 40,
    grid: true,
    line: false,
    tickSize: 0
  },
  marks: [
    Plot.areaY(forecast, {
      x: "forecast_date",
      y: "wind_speed_max_kmh",
      fill: dhColors.cyan,
      fillOpacity: 0.2,
      curve: "catmull-rom"
    }),
    Plot.lineY(forecast, {
      x: "forecast_date",
      y: "wind_speed_max_kmh",
      stroke: dhColors.cyan,
      strokeWidth: 3,
      curve: "catmull-rom"
    }),
    Plot.dot(forecast, {
      x: "forecast_date",
      y: "wind_speed_max_kmh",
      fill: dhColors.cyan,
      stroke: dhColors.bgCard,
      strokeWidth: 2,
      r: 6,
      tip: {
        format: {
          x: d => d.toLocaleDateString('en', {weekday: 'long', month: 'short', day: 'numeric'}),
          y: d => d.toFixed(1) + " km/h",
          fill: false,
          stroke: false
        }
      }
    }),
    Plot.text(forecast, {
      x: "forecast_date",
      y: "wind_speed_max_kmh",
      text: d => d.wind_speed_max_kmh.toFixed(0),
      dy: -12,
      fill: dhColors.textMuted,
      fontSize: 10
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
  temp_min: d.temperature_min_c,
  temp_avg: d.temperature_avg_c,
  temp_max: d.temperature_max_c,
  temp_category: d.temperature_category,
  precipitation: d.precipitation_mm,
  precip_category: d.precipitation_category,
  wind: d.wind_speed_max_kmh,
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
    date: d => d ? new Date(d).toLocaleDateString() : "—",
    temp_avg: d => d != null ? Number(d).toFixed(1) : "—",
    precipitation: d => d != null ? Number(d).toFixed(1) : "—",
    wind: d => d != null ? Number(d).toFixed(1) : "—",
    comfort: d => d != null ? Number(d).toFixed(0) : "—",
    is_weekend: d => d ? "Yes" : "No"
  }
})
```

---

<div class="tip">

**Data Source:** [Open-Meteo API](https://open-meteo.com/) - Free weather forecast data for Stockholm (59.33°N, 18.07°E).

</div>

