---
title: Customer Analytics
---

# Customer Analytics

Deep dive into customer behavior, segmentation, and lifetime value.

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
  border: "#3a4a5d"
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
    label: "Customer Count",
    grid: true,
    line: false,
    tickSize: 0
  },
  marks: [
    Plot.barY(segmentData, {
      x: "customer_segment",
      y: "customer_count",
      fill: d => segmentColors[d.customer_segment] || dhColors.gold,
      rx: 4,
      tip: {
        format: {
          y: d => d.toLocaleString() + " customers",
          fill: false
        }
      }
    }),
    Plot.text(segmentData, {
      x: "customer_segment",
      y: "customer_count",
      text: d => d.customer_count,
      dy: -10,
      fill: dhColors.textMuted,
      fontSize: 12,
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
    label: "Revenue ($)",
    grid: true,
    line: false,
    tickSize: 0,
    tickFormat: d => "$" + (d/1000).toFixed(0) + "k"
  },
  marks: [
    Plot.barY(segmentData, {
      x: "customer_segment",
      y: "segment_revenue",
      fill: d => segmentColors[d.customer_segment] || dhColors.gold,
      rx: 4,
      tip: {
        format: {
          y: d => "$" + d.toLocaleString(),
          fill: false
        }
      }
    }),
    Plot.text(segmentData, {
      x: "customer_segment",
      y: "segment_revenue",
      text: d => "$" + (d.segment_revenue/1000).toFixed(1) + "k",
      dy: -10,
      fill: dhColors.textMuted,
      fontSize: 11,
      fontWeight: 600
    })
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
  width: 600,
  height: 260,
  marginLeft: 100,
  marginTop: 20,
  marginBottom: 40,
  marginRight: 50,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Number of Customers",
    labelOffset: 36,
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
    Plot.barX(byCity, {
      y: "city",
      x: "customers",
      fill: dhColors.blue,
      rx: 3,
      sort: {y: "-x"},
      tip: {
        format: {
          x: d => d.toLocaleString() + " customers",
          fill: false
        }
      }
    }),
    Plot.text(byCity, {
      y: "city",
      x: "customers",
      text: d => d.customers,
      dx: 8,
      fill: dhColors.textMuted,
      fontSize: 10
    })
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
  width: 700,
  height: 380,
  marginTop: 30,
  marginBottom: 50,
  marginLeft: 70,
  marginRight: 30,
  style: {
    background: "transparent",
    color: dhColors.text,
    fontSize: "12px",
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  x: {
    label: "Total Orders",
    labelOffset: 40,
    grid: true,
    line: false,
    tickSize: 0
  },
  y: {
    label: "Total Revenue ($)",
    labelOffset: 55,
    grid: true,
    line: false,
    tickSize: 0,
    tickFormat: d => "$" + (d/1000).toFixed(0) + "k"
  },
  color: {
    legend: true,
    domain: ["VIP", "Regular", "New", "Inactive"],
    range: [dhColors.gold, dhColors.blue, dhColors.green, dhColors.purple]
  },
  marks: [
    Plot.dot(allCustomers.filter(d => d.total_orders > 0), {
      x: "total_orders",
      y: "total_revenue",
      fill: "customer_segment",
      stroke: dhColors.bgCard,
      strokeWidth: 2,
      r: 10,
      fillOpacity: 0.85,
      tip: {
        format: {
          x: d => d + " orders",
          y: d => "$" + d.toLocaleString(),
          fill: false
        }
      }
    })
  ]
})
```

