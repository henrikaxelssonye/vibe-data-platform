---
title: Overview
---

# Vibe Data Platform Dashboard

Welcome to the Vibe Data Platform analytics dashboard. This dashboard provides insights into customer behavior, sales performance, and weather patterns.

```js
import * as Plot from "npm:@observablehq/plot";
import {DuckDBClient} from "npm:@observablehq/duckdb";
```

```js
// Initialize DuckDB with our data files
const db = DuckDBClient.of({
  customer_orders: FileAttachment("data/customer_orders.parquet"),
  orders_summary: FileAttachment("data/orders_summary.parquet"),
  weather_daily: FileAttachment("data/weather_daily.parquet")
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
  FROM customer_orders
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
  FROM customer_orders
  GROUP BY customer_segment
  ORDER BY count DESC
`);
```

```js
Plot.plot({
  title: "Customers by Segment",
  width: 500,
  height: 300,
  marginLeft: 100,
  x: {label: "Number of Customers"},
  y: {label: null},
  marks: [
    Plot.barX(segments, {
      y: "customer_segment",
      x: "count",
      fill: "customer_segment",
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

## Revenue by Customer

```js
const revenueByCustomer = await db.query(`
  SELECT
    customer_name,
    total_revenue
  FROM customer_orders
  WHERE total_revenue > 0
  ORDER BY total_revenue DESC
  LIMIT 10
`);
```

```js
Plot.plot({
  title: "Top Customers by Revenue",
  width: 600,
  height: 300,
  marginLeft: 80,
  x: {label: "Revenue ($)", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(revenueByCustomer, {
      y: "customer_name",
      x: "total_revenue",
      fill: "steelblue",
      tip: true,
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```

## Weather Forecast

```js
const weather = await db.query(`
  SELECT
    forecast_date,
    temperature_avg,
    precipitation_mm,
    weather_comfort_score
  FROM weather_daily
  ORDER BY forecast_date
  LIMIT 7
`);
```

```js
Plot.plot({
  title: "7-Day Weather Forecast",
  width: 700,
  height: 250,
  x: {type: "utc", label: "Date"},
  y: {label: "Temperature (°C)", grid: true},
  marks: [
    Plot.lineY(weather, {x: "forecast_date", y: "temperature_avg", stroke: "orange", strokeWidth: 2}),
    Plot.dot(weather, {x: "forecast_date", y: "temperature_avg", fill: "orange", tip: true})
  ]
})
```

---

<div class="tip">

**Data Sources**: Customer and order data from internal systems. Weather data from [Open-Meteo API](https://open-meteo.com/).

**Last Updated**: Data refreshes automatically when the dbt pipeline runs.

</div>

<style>
.big {
  font-size: 2.5rem;
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

.kpi-card {
  text-align: center;
}

.kpi-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--theme-foreground-focus);
  line-height: 1.2;
  margin-top: 0.5rem;
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

  .kpi-value {
    font-size: 1.75rem;
  }
}
</style>
