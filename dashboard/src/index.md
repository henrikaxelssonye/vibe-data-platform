---
title: Overview
---

# Vibe Data Platform

Executive summary of customer, sales, and weather metrics.

```js
import * as Plot from "npm:@observablehq/plot";
import {DuckDBClient} from "npm:@observablehq/duckdb";

// Dark Horse Analytics color palette
const dhColors = {
  gold: "#c6b356",
  goldDim: "#9d8e45",
  blue: "#60a5fa",
  green: "#4ade80",
  pink: "#f472b6",
  purple: "#a78bfa",
  orange: "#fb923c",
  text: "#f1f1ef",
  textMuted: "#a0aab8",
  bgCard: "#2a3a4d",
  border: "#3a4a5d"
};

// Segment color scale
const segmentColors = {
  "VIP": dhColors.gold,
  "Regular": dhColors.blue,
  "New": dhColors.green,
  "Inactive": dhColors.purple
};
```

```js
// Initialize DuckDB with the database file directly
const db = DuckDBClient.of({
  vibe: FileAttachment("data/vibe.duckdb")
});
```

## Key Metrics

```js
// Fetch summary metrics
const customerMetrics = await db.query(`
  SELECT
    COUNT(*) as total_customers,
    COUNT(CASE WHEN total_orders > 0 THEN 1 END) as active_customers,
    SUM(total_revenue) as total_revenue,
    SUM(total_orders) as total_orders
  FROM vibe.customer_orders
`);

// Get first row - convert to array first to get proper scalar values
const metricsArray = Array.from(customerMetrics);
const metrics = metricsArray[0];

// Format numbers for display (values are already scalars after Array.from)
const totalCustomers = Number(metrics?.total_customers ?? 0);
const activeCustomers = Number(metrics?.active_customers ?? 0);
const totalRevenue = Number(metrics?.total_revenue ?? 0);
const totalOrders = Number(metrics?.total_orders ?? 0);
```

<div class="grid grid-cols-4">
  <div class="card kpi-card">
    <h2>Total Customers</h2>
    <div class="kpi-value">${totalCustomers}</div>
  </div>
  <div class="card kpi-card">
    <h2>Active Customers</h2>
    <div class="kpi-value">${activeCustomers}</div>
  </div>
  <div class="card kpi-card">
    <h2>Total Revenue</h2>
    <div class="kpi-value">$${totalRevenue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
  </div>
  <div class="card kpi-card">
    <h2>Total Orders</h2>
    <div class="kpi-value">${totalOrders}</div>
  </div>
</div>

## Customer Segments

```js
const segments = await db.query(`
  SELECT
    customer_segment,
    COUNT(*) as count
  FROM vibe.customer_orders
  GROUP BY customer_segment
  ORDER BY count DESC
`);
```

```js
Plot.plot({
  width: 500,
  height: 280,
  marginLeft: 100,
  marginTop: 30,
  marginBottom: 40,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Number of Customers",
    labelOffset: 36,
    tickFormat: "d",
    grid: true,
    line: false,
    tickSize: 0
  },
  y: {
    label: null,
    tickSize: 0,
    line: false
  },
  marks: [
    Plot.barX(segments, {
      y: "customer_segment",
      x: "count",
      fill: d => segmentColors[d.customer_segment] || dhColors.gold,
      rx: 3,
      tip: {
        format: {
          x: d => d.toLocaleString(),
          fill: false
        }
      }
    }),
    Plot.text(segments, {
      y: "customer_segment",
      x: "count",
      text: d => d.count.toLocaleString(),
      dx: 8,
      fill: dhColors.textMuted,
      fontSize: 11
    })
  ]
})
```

## Revenue by Customer

```js
const revenueByCustomer = await db.query(`
  SELECT
    customer_name,
    total_revenue
  FROM vibe.customer_orders
  WHERE total_revenue > 0
  ORDER BY total_revenue DESC
  LIMIT 10
`);
```

```js
Plot.plot({
  width: 600,
  height: 320,
  marginLeft: 90,
  marginTop: 30,
  marginBottom: 40,
  marginRight: 60,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Revenue ($)",
    labelOffset: 36,
    tickFormat: d => "$" + (d/1000).toFixed(0) + "k",
    grid: true,
    line: false,
    tickSize: 0
  },
  y: {
    label: null,
    tickSize: 0,
    line: false
  },
  marks: [
    Plot.barX(revenueByCustomer, {
      y: "customer_name",
      x: "total_revenue",
      fill: dhColors.gold,
      rx: 3,
      sort: {y: "-x"},
      tip: {
        format: {
          x: d => "$" + d.toLocaleString(),
          fill: false
        }
      }
    }),
    Plot.text(revenueByCustomer, {
      y: "customer_name",
      x: "total_revenue",
      text: d => "$" + (d.total_revenue/1000).toFixed(1) + "k",
      dx: 8,
      fill: dhColors.textMuted,
      fontSize: 10
    })
  ]
})
```

## Weather Forecast

```js
const weather = await db.query(`
  SELECT
    forecast_date,
    temperature_avg_c,
    precipitation_mm,
    weather_comfort_score
  FROM vibe.weather_daily
  ORDER BY forecast_date
  LIMIT 7
`);
```

```js
Plot.plot({
  width: 700,
  height: 260,
  marginTop: 30,
  marginBottom: 45,
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
    labelOffset: 38,
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
    Plot.areaY(weather, {
      x: "forecast_date",
      y: "temperature_avg_c",
      fill: dhColors.gold,
      fillOpacity: 0.15,
      curve: "catmull-rom"
    }),
    Plot.lineY(weather, {
      x: "forecast_date",
      y: "temperature_avg_c",
      stroke: dhColors.gold,
      strokeWidth: 3,
      curve: "catmull-rom"
    }),
    Plot.dot(weather, {
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
    })
  ]
})
```

---

<div class="tip">

**Data Sources**: Customer and order data from internal systems. Weather data from [Open-Meteo API](https://open-meteo.com/).

**Last Updated**: Data refreshes automatically when the dbt pipeline runs.

</div>
