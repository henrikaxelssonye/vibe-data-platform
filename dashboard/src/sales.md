---
title: Sales Performance
---

# Sales Performance

Track order trends, product performance, and revenue metrics.

```js
import * as Plot from "npm:@observablehq/plot";
import {DuckDBClient} from "npm:@observablehq/duckdb";
import {Inputs} from "npm:@observablehq/inputs";
```

```js
const db = DuckDBClient.of({
  customer_orders: FileAttachment("data/customer_orders.parquet"),
  orders_summary: FileAttachment("data/orders_summary.parquet")
});
```

## Sales Summary

```js
const salesMetrics = await db.query(`
  SELECT
    SUM(total_orders) as total_orders,
    SUM(total_revenue) as total_revenue,
    SUM(completed_orders) as completed_orders,
    SUM(pending_orders) as pending_orders,
    SUM(cancelled_orders) as cancelled_orders,
    AVG(total_revenue) as avg_customer_value
  FROM customer_orders
`);

const sales = salesMetrics[0];
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Total Orders</h2>
    <span class="big">${sales?.total_orders ?? "—"}</span>
  </div>
  <div class="card">
    <h2>Total Revenue</h2>
    <span class="big">$${sales?.total_revenue?.toLocaleString() ?? "—"}</span>
  </div>
  <div class="card">
    <h2>Avg Customer Value</h2>
    <span class="big">$${sales?.avg_customer_value?.toFixed(0) ?? "—"}</span>
  </div>
  <div class="card">
    <h2>Completion Rate</h2>
    <span class="big">${sales?.total_orders > 0 ? ((sales.completed_orders / sales.total_orders) * 100).toFixed(0) : 0}%</span>
  </div>
</div>

## Order Status Breakdown

```js
const statusData = [
  { status: "Completed", count: sales?.completed_orders ?? 0, color: "#22c55e" },
  { status: "Pending", count: sales?.pending_orders ?? 0, color: "#f59e0b" },
  { status: "Cancelled", count: sales?.cancelled_orders ?? 0, color: "#ef4444" }
].filter(d => d.count > 0);
```

<div class="grid grid-cols-2">

```js
Plot.plot({
  title: "Orders by Status",
  width: 400,
  height: 300,
  marks: [
    Plot.barY(statusData, {
      x: "status",
      y: "count",
      fill: "color",
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

```js
Plot.plot({
  title: "Status Distribution",
  width: 400,
  height: 300,
  marks: [
    Plot.barX(statusData, Plot.stackX({
      x: "count",
      fill: "status",
      tip: true
    }))
  ],
  color: {
    domain: ["Completed", "Pending", "Cancelled"],
    range: ["#22c55e", "#f59e0b", "#ef4444"],
    legend: true
  }
})
```

</div>

## Revenue by Customer

```js
const revenueData = await db.query(`
  SELECT
    customer_name,
    total_revenue,
    total_orders,
    customer_segment
  FROM customer_orders
  WHERE total_revenue > 0
  ORDER BY total_revenue DESC
`);
```

```js
Plot.plot({
  title: "Revenue Distribution by Customer",
  width: 700,
  height: 350,
  marginLeft: 100,
  x: {label: "Revenue ($)", grid: true},
  y: {label: null},
  color: {legend: true},
  marks: [
    Plot.barX(revenueData, {
      y: "customer_name",
      x: "total_revenue",
      fill: "customer_segment",
      tip: true,
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```

## Orders per Customer

```js
Plot.plot({
  title: "Order Volume by Customer",
  width: 700,
  height: 350,
  marginLeft: 100,
  x: {label: "Number of Orders", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(revenueData, {
      y: "customer_name",
      x: "total_orders",
      fill: "steelblue",
      tip: true,
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```

## Customer Contribution

```js
// Calculate revenue percentages
const totalRev = revenueData.reduce((sum, d) => sum + d.total_revenue, 0);
const withPct = revenueData.map(d => ({
  ...d,
  revenue_pct: (d.total_revenue / totalRev * 100).toFixed(1)
}));
```

```js
Inputs.table(withPct, {
  columns: [
    "customer_name",
    "customer_segment",
    "total_orders",
    "total_revenue",
    "revenue_pct"
  ],
  header: {
    customer_name: "Customer",
    customer_segment: "Segment",
    total_orders: "Orders",
    total_revenue: "Revenue",
    revenue_pct: "% of Total"
  },
  format: {
    total_revenue: d => `$${d.toLocaleString()}`,
    revenue_pct: d => `${d}%`
  },
  sort: "total_revenue",
  reverse: true
})
```

## Insights

<div class="note">

**Key Observations:**
- The dashboard shows aggregated customer order data
- VIP customers typically generate the highest revenue
- Monitor pending orders for potential fulfillment issues
- Track cancellation rates to identify quality concerns

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

.grid {
  display: grid;
  gap: 1rem;
  margin: 1.5rem 0;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 768px) {
  .grid-cols-2, .grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
