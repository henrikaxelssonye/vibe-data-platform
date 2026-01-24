---
title: Customer Analytics
---

# Customer Analytics

Deep dive into customer behavior, segmentation, and lifetime value.

```js
import * as Plot from "npm:@observablehq/plot";
import {DuckDBClient} from "npm:@observablehq/duckdb";
import * as Inputs from "npm:@observablehq/inputs";
```

```js
const db = DuckDBClient.of({
  customer_orders: FileAttachment("data/customer_orders.parquet"),
  orders_summary: FileAttachment("data/orders_summary.parquet")
});
```

## Customer Overview

```js
const allCustomersResult = await db.query(`
  SELECT * FROM customer_orders
  ORDER BY total_revenue DESC
`);

// Convert DuckDB Arrow result to JS array
const allCustomers = Array.from(allCustomersResult);

const segments = [...new Set(allCustomers.map(d => d.customer_segment))];
```

```js
const segmentFilter = view(Inputs.select(["All", ...segments], {
  label: "Filter by Segment",
  value: "All"
}));
```

```js
const customers = segmentFilter === "All"
  ? allCustomers
  : allCustomers.filter(d => d.customer_segment === segmentFilter);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Customers Shown</h2>
    <span class="big">${customers.length}</span>
  </div>
  <div class="card">
    <h2>Total Revenue</h2>
    <span class="big">$${customers.reduce((sum, c) => sum + (c.total_revenue || 0), 0).toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Avg Orders/Customer</h2>
    <span class="big">${(customers.reduce((sum, c) => sum + (c.total_orders || 0), 0) / customers.length || 0).toFixed(1)}</span>
  </div>
</div>

## Segment Distribution

```js
const segmentData = await db.query(`
  SELECT
    customer_segment,
    COUNT(*) as customer_count,
    SUM(total_revenue) as segment_revenue,
    AVG(total_orders) as avg_orders
  FROM customer_orders
  GROUP BY customer_segment
  ORDER BY segment_revenue DESC
`);
```

<div class="grid grid-cols-2">

```js
Plot.plot({
  title: "Customers by Segment",
  width: 400,
  height: 300,
  marks: [
    Plot.barY(segmentData, {
      x: "customer_segment",
      y: "customer_count",
      fill: "customer_segment",
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

```js
Plot.plot({
  title: "Revenue by Segment",
  width: 400,
  height: 300,
  marks: [
    Plot.barY(segmentData, {
      x: "customer_segment",
      y: "segment_revenue",
      fill: "customer_segment",
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

</div>

## Geographic Distribution

```js
const byCity = await db.query(`
  SELECT
    city,
    country,
    COUNT(*) as customers,
    SUM(total_revenue) as revenue
  FROM customer_orders
  GROUP BY city, country
  ORDER BY revenue DESC
`);
```

```js
Plot.plot({
  title: "Customers by City",
  width: 600,
  height: 250,
  marginLeft: 100,
  x: {label: "Number of Customers", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(byCity, {
      y: "city",
      x: "customers",
      fill: "steelblue",
      tip: true,
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```

## Customer Details

```js
Inputs.table(customers, {
  columns: [
    "customer_name",
    "email",
    "city",
    "customer_segment",
    "total_orders",
    "total_revenue",
    "completed_orders",
    "pending_orders"
  ],
  header: {
    customer_name: "Name",
    email: "Email",
    city: "City",
    customer_segment: "Segment",
    total_orders: "Orders",
    total_revenue: "Revenue",
    completed_orders: "Completed",
    pending_orders: "Pending"
  },
  format: {
    total_revenue: d => d ? `$${d.toLocaleString()}` : "—"
  },
  sort: "total_revenue",
  reverse: true,
  rows: 20
})
```

## Customer Value Analysis

```js
Plot.plot({
  title: "Customer Value: Orders vs Revenue",
  width: 700,
  height: 400,
  grid: true,
  x: {label: "Total Orders"},
  y: {label: "Total Revenue ($)"},
  color: {legend: true},
  marks: [
    Plot.dot(allCustomers.filter(d => d.total_orders > 0), {
      x: "total_orders",
      y: "total_revenue",
      fill: "customer_segment",
      r: 8,
      tip: true,
      title: d => `${d.customer_name}\n${d.total_orders} orders\n$${d.total_revenue}`
    })
  ]
})
```

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

.grid {
  display: grid;
  gap: 1rem;
  margin: 1.5rem 0;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 768px) {
  .grid-cols-2, .grid-cols-3 {
    grid-template-columns: 1fr;
  }
}
</style>
