#!/usr/bin/env python3
"""
Export dbt models to Parquet files for the Observable Framework dashboard.

This script reads data from the DuckDB database created by dbt and exports
key tables to Parquet format for efficient loading in the browser via DuckDB-WASM.
"""

import argparse
import sys
from pathlib import Path

import duckdb
import pandas as pd


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "vibe.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "dashboard" / "src" / "data"

# Tables to export with their queries
EXPORTS = {
    "customer_orders": """
        SELECT
            co.customer_id,
            co.customer_name,
            co.email,
            co.city,
            co.country,
            co.customer_since,
            co.total_orders,
            co.total_revenue,
            co.completed_orders,
            os.pending_orders,
            os.cancelled_orders,
            co.first_order_date,
            co.last_order_date,
            co.customer_segment
        FROM customer_orders co
        LEFT JOIN orders_summary os ON co.customer_id = os.customer_id
    """,
    "orders_summary": """
        SELECT
            customer_id,
            total_orders,
            total_revenue,
            completed_orders,
            pending_orders,
            cancelled_orders,
            first_order_date,
            last_order_date
        FROM orders_summary
    """,
    "weather_daily": """
        SELECT
            forecast_date,
            temperature_min_c as temperature_min,
            temperature_max_c as temperature_max,
            temperature_avg_c as temperature_avg,
            precipitation_mm,
            wind_speed_max_kmh as wind_speed_avg,
            temperature_category,
            precipitation_category,
            wind_category,
            weather_comfort_score,
            year,
            month,
            day,
            day_of_week,
            is_weekend
        FROM weather_daily
    """,
}


def create_sample_data() -> dict[str, pd.DataFrame]:
    """Create sample data for development when database doesn't exist."""
    print("Creating sample data for development...")

    customer_orders = pd.DataFrame({
        "customer_id": [101, 102, 103, 104, 105],
        "customer_name": ["Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Eve Davis"],
        "email": ["alice@example.com", "bob@example.com", "carol@example.com", "david@example.com", "eve@example.com"],
        "city": ["Stockholm", "Gothenburg", "Malmo", "Uppsala", "Linkoping"],
        "country": ["Sweden", "Sweden", "Sweden", "Sweden", "Sweden"],
        "customer_created_at": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]),
        "total_orders": [5, 3, 7, 2, 4],
        "total_revenue": [1250.00, 750.00, 1875.50, 450.00, 1100.00],
        "completed_orders": [4, 2, 6, 1, 3],
        "pending_orders": [1, 1, 1, 1, 1],
        "cancelled_orders": [0, 0, 0, 0, 0],
        "first_order_date": pd.to_datetime(["2024-01-10", "2024-01-12", "2024-01-08", "2024-01-15", "2024-01-11"]),
        "last_order_date": pd.to_datetime(["2024-01-20", "2024-01-18", "2024-01-22", "2024-01-16", "2024-01-19"]),
        "customer_segment": ["VIP", "Regular", "VIP", "New", "Regular"],
    })

    orders_summary = pd.DataFrame({
        "customer_id": [101, 102, 103, 104, 105],
        "total_orders": [5, 3, 7, 2, 4],
        "total_revenue": [1250.00, 750.00, 1875.50, 450.00, 1100.00],
        "completed_orders": [4, 2, 6, 1, 3],
        "pending_orders": [1, 1, 1, 1, 1],
        "cancelled_orders": [0, 0, 0, 0, 0],
        "first_order_date": pd.to_datetime(["2024-01-10", "2024-01-12", "2024-01-08", "2024-01-15", "2024-01-11"]),
        "last_order_date": pd.to_datetime(["2024-01-20", "2024-01-18", "2024-01-22", "2024-01-16", "2024-01-19"]),
    })

    import datetime
    base_date = datetime.date.today()
    weather_daily = pd.DataFrame({
        "forecast_date": pd.date_range(base_date, periods=7),
        "temperature_min": [-2.0, -1.0, 0.0, 1.0, -1.0, -3.0, -2.0],
        "temperature_max": [3.0, 4.0, 5.0, 6.0, 4.0, 2.0, 3.0],
        "temperature_avg": [0.5, 1.5, 2.5, 3.5, 1.5, -0.5, 0.5],
        "precipitation_mm": [0.0, 2.5, 0.5, 0.0, 5.0, 1.0, 0.0],
        "wind_speed_avg": [15.0, 20.0, 10.0, 8.0, 25.0, 18.0, 12.0],
        "temperature_category": ["cold", "cold", "cold", "cold", "cold", "cold", "cold"],
        "precipitation_category": ["dry", "light", "light", "dry", "moderate", "light", "dry"],
        "wind_category": ["moderate", "moderate", "light", "light", "strong", "moderate", "moderate"],
        "weather_comfort_score": [45.0, 35.0, 55.0, 65.0, 25.0, 40.0, 50.0],
        "year": [base_date.year] * 7,
        "month": [base_date.month] * 7,
        "day": list(range(base_date.day, base_date.day + 7)),
        "day_of_week": ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Tuesday"],
        "is_weekend": [False, False, False, True, True, False, False],
    })

    return {
        "customer_orders": customer_orders,
        "orders_summary": orders_summary,
        "weather_daily": weather_daily,
    }


def export_from_database(db_path: Path) -> dict[str, pd.DataFrame]:
    """Export data from DuckDB database."""
    print(f"Connecting to database: {db_path}")
    conn = duckdb.connect(str(db_path), read_only=True)

    data = {}
    for name, query in EXPORTS.items():
        try:
            print(f"  Exporting {name}...")
            df = conn.execute(query).fetchdf()
            data[name] = df
            print(f"    -> {len(df)} rows")
        except Exception as e:
            print(f"    -> Error: {e}")
            # Try to get sample data for this table
            sample = create_sample_data()
            if name in sample:
                data[name] = sample[name]
                print(f"    -> Using sample data: {len(data[name])} rows")

    conn.close()
    return data


def save_to_parquet(data: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Save DataFrames to Parquet files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, df in data.items():
        output_path = output_dir / f"{name}.parquet"
        df.to_parquet(output_path, index=False)
        print(f"  Saved {output_path} ({len(df)} rows, {output_path.stat().st_size / 1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Export dbt models to Parquet for dashboard")
    parser.add_argument("--sample", action="store_true", help="Generate sample data (skip database)")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="DuckDB database path")
    args = parser.parse_args()

    print("=" * 60)
    print("Dashboard Data Export")
    print("=" * 60)

    # Export data
    if args.sample or not args.db.exists():
        if not args.db.exists():
            print(f"Database not found at {args.db}")
        data = create_sample_data()
    else:
        data = export_from_database(args.db)

    # Save to Parquet
    print(f"\nSaving Parquet files to {args.output}...")
    save_to_parquet(data, args.output)

    print("\nExport complete!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
