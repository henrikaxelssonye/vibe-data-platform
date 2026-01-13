#!/usr/bin/env python3
"""
File Ingestion Utility for Vibe Data Platform

This script ingests CSV and Parquet files into DuckDB for use with dbt.
Configuration is read from config/sources.yml.

Usage:
    python scripts/ingest_files.py                    # Ingest all files
    python scripts/ingest_files.py --file data.csv   # Ingest specific file
    python scripts/ingest_files.py --list            # List available files
    python scripts/ingest_files.py --schema file.csv # Show schema of file
    python scripts/ingest_files.py --azure           # Also upload to Azure after ingestion
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import duckdb
import yaml

# Optional Azure support
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


def load_config() -> dict:
    """Load source configuration from config/sources.yml."""
    config_path = Path(__file__).parent.parent / "config" / "sources.yml"
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_db_path() -> Path:
    """Get the DuckDB database path."""
    return Path(__file__).parent.parent / "data" / "processed" / "vibe.duckdb"


def list_files(config: dict) -> None:
    """List all available data files."""
    base_path = Path(__file__).parent.parent

    print("\nAvailable Data Files:")
    print("-" * 60)

    file_configs = config.get("sources", {}).get("files", {})

    for file_type, type_config in file_configs.items():
        if not type_config.get("enabled", False):
            continue

        pattern = type_config.get("pattern", f"*.{file_type}")
        search_path = base_path / type_config.get("path", "data/raw/")

        files = list(search_path.glob(pattern))

        print(f"\n{file_type.upper()} Files ({search_path}):")
        if files:
            for f in files:
                size = f.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                print(f"  - {f.name} ({size_str})")
        else:
            print(f"  (no {file_type} files found)")


def show_schema(file_path: Path) -> None:
    """Show the schema of a data file."""
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return

    print(f"\nSchema for: {file_path.name}")
    print("-" * 50)

    con = duckdb.connect(":memory:")

    try:
        if file_path.suffix.lower() == ".csv":
            query = f"DESCRIBE SELECT * FROM read_csv_auto('{file_path}')"
        elif file_path.suffix.lower() == ".parquet":
            query = f"DESCRIBE SELECT * FROM read_parquet('{file_path}')"
        elif file_path.suffix.lower() == ".json":
            query = f"DESCRIBE SELECT * FROM read_json_auto('{file_path}')"
        else:
            print(f"Error: Unsupported file type: {file_path.suffix}")
            return

        result = con.execute(query).fetchall()

        print(f"{'Column':<30} {'Type':<20}")
        print("-" * 50)
        for row in result:
            print(f"{row[0]:<30} {row[1]:<20}")

        # Show row count
        if file_path.suffix.lower() == ".csv":
            count_query = f"SELECT COUNT(*) FROM read_csv_auto('{file_path}')"
        elif file_path.suffix.lower() == ".parquet":
            count_query = f"SELECT COUNT(*) FROM read_parquet('{file_path}')"
        elif file_path.suffix.lower() == ".json":
            count_query = f"SELECT COUNT(*) FROM read_json_auto('{file_path}')"

        row_count = con.execute(count_query).fetchone()[0]
        print(f"\nTotal rows: {row_count:,}")

    except Exception as e:
        print(f"Error reading file: {e}")
    finally:
        con.close()


def ingest_file(file_path: Path, table_name: str = None) -> bool:
    """Ingest a single file into DuckDB."""
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False

    # Generate table name from file name if not provided
    if table_name is None:
        table_name = f"raw_{file_path.stem.lower().replace('-', '_').replace(' ', '_')}"

    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nIngesting: {file_path.name}")
    print(f"  Table: {table_name}")
    print(f"  Database: {db_path}")

    con = duckdb.connect(str(db_path))

    try:
        # Read file based on extension
        if file_path.suffix.lower() == ".csv":
            read_func = f"read_csv_auto('{file_path}')"
        elif file_path.suffix.lower() == ".parquet":
            read_func = f"read_parquet('{file_path}')"
        elif file_path.suffix.lower() == ".json":
            read_func = f"read_json_auto('{file_path}')"
        else:
            print(f"  Error: Unsupported file type: {file_path.suffix}")
            return False

        # Create or replace table
        query = f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {read_func}"
        con.execute(query)

        # Get row count
        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        print(f"  Success: {row_count:,} rows loaded")

        # Log ingestion
        log_path = Path(__file__).parent.parent / "logs" / "pipeline_runs.log"
        with open(log_path, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] INGESTED file={file_path.name} table={table_name} rows={row_count}\n")

        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False
    finally:
        con.close()


def ingest_all(config: dict) -> dict:
    """Ingest all files from configured sources."""
    base_path = Path(__file__).parent.parent
    results = {"success": 0, "failed": 0}

    file_configs = config.get("sources", {}).get("files", {})

    for file_type, type_config in file_configs.items():
        if not type_config.get("enabled", False):
            continue

        pattern = type_config.get("pattern", f"*.{file_type}")
        search_path = base_path / type_config.get("path", "data/raw/")

        files = list(search_path.glob(pattern))

        for file_path in files:
            if ingest_file(file_path):
                results["success"] += 1
            else:
                results["failed"] += 1

    return results


def upload_to_azure(file_path: Path, config: dict) -> bool:
    """Upload a file to Azure Blob Storage after ingestion."""
    if not AZURE_AVAILABLE:
        print("  Warning: azure-storage-blob not installed, skipping Azure upload")
        return False

    azure_config = config.get("azure", {})
    if not azure_config.get("enabled", False):
        return False

    try:
        # Get credentials from environment
        connection_string = os.environ.get(
            azure_config.get("connection_string_env", "AZURE_STORAGE_CONNECTION_STRING")
        )
        account_name = os.environ.get(
            azure_config.get("storage_account_env", "AZURE_STORAGE_ACCOUNT")
        )
        account_key = os.environ.get(
            azure_config.get("storage_key_env", "AZURE_STORAGE_KEY")
        )

        if connection_string:
            blob_service = BlobServiceClient.from_connection_string(connection_string)
        elif account_name and account_key:
            account_url = f"https://{account_name}.blob.core.windows.net"
            blob_service = BlobServiceClient(account_url=account_url, credential=account_key)
        else:
            print("  Warning: Azure credentials not configured")
            return False

        # Upload to raw container
        container_name = azure_config.get("containers", {}).get("raw", "raw")
        container_client = blob_service.get_container_client(container_name)
        blob_client = container_client.get_blob_client(file_path.name)

        print(f"  Uploading to Azure: {container_name}/{file_path.name}")
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"  Azure upload successful")
        return True

    except Exception as e:
        print(f"  Warning: Azure upload failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Ingest data files into DuckDB")
    parser.add_argument("--file", help="Specific file to ingest")
    parser.add_argument("--table", help="Table name (default: raw_<filename>)")
    parser.add_argument("--list", action="store_true", help="List available files")
    parser.add_argument("--schema", help="Show schema of a file")
    parser.add_argument("--all", action="store_true", help="Ingest all files")
    parser.add_argument("--azure", action="store_true", help="Also upload to Azure after ingestion")
    args = parser.parse_args()

    config = load_config()

    if args.list:
        list_files(config)
        return

    if args.schema:
        base_path = Path(__file__).parent.parent
        file_path = base_path / "data" / "raw" / args.schema
        if not file_path.exists():
            file_path = Path(args.schema)
        show_schema(file_path)
        return

    if args.file:
        base_path = Path(__file__).parent.parent
        file_path = base_path / "data" / "raw" / args.file
        if not file_path.exists():
            file_path = Path(args.file)
        if ingest_file(file_path, args.table):
            if args.azure:
                upload_to_azure(file_path, config)
        return

    # Default: ingest all files
    results = ingest_all(config)
    print(f"\n{'=' * 50}")
    print(f"Ingestion Complete: {results['success']} succeeded, {results['failed']} failed")

    # Upload to Azure if requested
    if args.azure and results['success'] > 0:
        print("\nUploading to Azure Blob Storage...")
        base_path = Path(__file__).parent.parent
        raw_path = base_path / "data" / "raw"
        azure_success = 0
        for pattern in ["*.csv", "*.parquet", "*.json"]:
            for f in raw_path.glob(pattern):
                if upload_to_azure(f, config):
                    azure_success += 1
        print(f"Azure upload: {azure_success} files uploaded")


if __name__ == "__main__":
    main()
