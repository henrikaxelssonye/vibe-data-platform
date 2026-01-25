---
title: Sales Performance
---

# Sales Performance

Track order trends, product performance, and revenue metrics.

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
  text: "#f1f1ef",
  textMuted: "#a0aab8",
  bgCard: "#2a3a4d",
  border: "#3a4a5d",
  success: "#4ade80",
  warning: "#fbbf24",
  danger: "#f87171"
};

const segmentColors = {
  "VIP": dhColors.gold,
  "Regular": dhColors.blue,
  "New": dhColors.green,
  "Inactive": dhColors.purple
};
```

```js
const db = DuckDBClient.of({
  customer_orders: FileAttachment("data/customer_orders.parquet"),
  orders_summary: FileAttachment("data/orders_summary.parquet")
});
```

## Sales Summary

```js
const salesMetricsResult = await db.query(`
  SELECT
    SUM(total_orders) as total_orders,
    SUM(total_revenue) as total_revenue,
    SUM(completed_orders) as completed_orders,
    SUM(pending_orders) as pending_orders,
    SUM(cancelled_orders) as cancelled_orders,
    AVG(total_revenue) as avg_customer_value
  FROM customer_orders
`);

// Convert DuckDB Arrow result to JS array
const salesMetrics = Array.from(salesMetricsResult);
const salesRow = salesMetrics[0];

// Convert BigInt/typed values to Numbers
const sales = {
  total_orders: Number(salesRow?.total_orders ?? 0),
  total_revenue: Number(salesRow?.total_revenue ?? 0),
  completed_orders: Number(salesRow?.completed_orders ?? 0),
  pending_orders: Number(salesRow?.pending_orders ?? 0),
  cancelled_orders: Number(salesRow?.cancelled_orders ?? 0),
  avg_customer_value: Number(salesRow?.avg_customer_value ?? 0)
};
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Total Orders</h2>
    <span class="big">${sales.total_orders}</span>
  </div>
  <div class="card">
    <h2>Total Revenue</h2>
    <span class="big">$${sales.total_revenue.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Avg Customer Value</h2>
    <span class="big">$${sales.avg_customer_value.toFixed(0)}</span>
  </div>
  <div class="card">
    <h2>Completion Rate</h2>
    <span class="big">${sales.total_orders > 0 ? ((sales.completed_orders / sales.total_orders) * 100).toFixed(0) : 0}%</span>
  </div>
</div>

## Order Status Breakdown

```js
const statusData = [
  { status: "Completed", count: sales?.completed_orders ?? 0, color: dhColors.success },
  { status: "Pending", count: sales?.pending_orders ?? 0, color: dhColors.warning },
  { status: "Cancelled", count: sales?.cancelled_orders ?? 0, color: dhColors.danger }
].filter(d => d.count > 0);
```

<div class="grid grid-cols-2">

```js
Plot.plot({
  width: 400,
  height: 280,
  marginTop: 20,
  marginBottom: 50,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: null,
    tickSize: 0,
    line: false
  },
  y: {
    label: "Number of Orders",
    grid: true,
    line: false,
    tickSize: 0
  },
  marks: [
    Plot.barY(statusData, {
      x: "status",
      y: "count",
      fill: "color",
      rx: 4,
      tip: {
        format: {
          y: d => d.toLocaleString() + " orders",
          fill: false
        }
      }
    }),
    Plot.text(statusData, {
      x: "status",
      y: "count",
      text: d => d.count.toLocaleString(),
      dy: -12,
      fill: dhColors.textMuted,
      fontSize: 13,
      fontWeight: 600
    })
  ]
})
```

```js
Plot.plot({
  width: 400,
  height: 280,
  marginTop: 20,
  marginBottom: 50,
  marginLeft: 20,
  marginRight: 20,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: null,
    tickSize: 0,
    line: false,
    axis: null
  },
  y: {
    label: null,
    axis: null
  },
  marks: [
    Plot.barX(statusData, Plot.stackX({
      x: "count",
      fill: "status",
      rx: 4,
      inset: 0.5,
      tip: {
        format: {
          x: d => d.toLocaleString() + " orders",
          fill: false
        }
      }
    })),
    Plot.text(statusData, Plot.stackX({
      x: "count",
      text: d => d.status + "\n" + d.count,
      fill: dhColors.bgCard,
      fontSize: 11,
      fontWeight: 600
    }))
  ],
  color: {
    domain: ["Completed", "Pending", "Cancelled"],
    range: [dhColors.success, dhColors.warning, dhColors.danger],
    legend: true
  }
})
```

</div>

## Revenue by Customer

```js
const revenueDataResult = await db.query(`
  SELECT
    customer_name,
    total_revenue,
    total_orders,
    customer_segment
  FROM customer_orders
  WHERE total_revenue > 0
  ORDER BY total_revenue DESC
`);

// Convert DuckDB Arrow result to JS array
const revenueData = Array.from(revenueDataResult);
```

```js
Plot.plot({
  width: 700,
  height: 340,
  marginLeft: 100,
  marginTop: 20,
  marginBottom: 45,
  marginRight: 60,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Revenue ($)",
    labelOffset: 38,
    grid: true,
    line: false,
    tickSize: 0,
    tickFormat: d => "$" + (d/1000).toFixed(0) + "k"
  },
  y: {
    label: null,
    tickSize: 0,
    line: false
  },
  color: {
    legend: true,
    domain: ["VIP", "Regular", "New", "Inactive"],
    range: [dhColors.gold, dhColors.blue, dhColors.green, dhColors.purple]
  },
  marks: [
    Plot.barX(revenueData, {
      y: "customer_name",
      x: "total_revenue",
      fill: "customer_segment",
      rx: 3,
      sort: {y: "-x"},
      tip: {
        format: {
          x: d => "$" + d.toLocaleString(),
          fill: false
        }
      }
    }),
    Plot.text(revenueData.slice(0, 5), {
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

## Orders per Customer

```js
Plot.plot({
  width: 700,
  height: 340,
  marginLeft: 100,
  marginTop: 20,
  marginBottom: 45,
  marginRight: 50,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Number of Orders",
    labelOffset: 38,
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
    Plot.barX(revenueData, {
      y: "customer_name",
      x: "total_orders",
      fill: dhColors.blue,
      rx: 3,
      sort: {y: "-x"},
      tip: {
        format: {
          x: d => d.toLocaleString() + " orders",
          fill: false
        }
      }
    }),
    Plot.text(revenueData.slice(0, 5), {
      y: "customer_name",
      x: "total_orders",
      text: d => d.total_orders,
      dx: 8,
      fill: dhColors.textMuted,
      fontSize: 10
    })
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

