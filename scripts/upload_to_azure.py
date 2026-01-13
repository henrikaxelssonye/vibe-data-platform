#!/usr/bin/env python3
"""
Azure Blob Storage Upload Utility for Vibe Data Platform

This script uploads local data files and DuckDB database to Azure Blob Storage.

Usage:
    python scripts/upload_to_azure.py --all          # Upload all data
    python scripts/upload_to_azure.py --raw          # Upload raw data files only
    python scripts/upload_to_azure.py --db           # Upload DuckDB database only
    python scripts/upload_to_azure.py --file x.csv   # Upload specific file
    python scripts/upload_to_azure.py --list         # List files in Azure

Environment Variables (or use .env file):
    AZURE_STORAGE_ACCOUNT       - Storage account name
    AZURE_STORAGE_KEY           - Storage account access key
    AZURE_STORAGE_CONNECTION_STRING - Alternative: full connection string
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
except ImportError:
    print("Error: azure-storage-blob not installed.")
    print("Install with: pip install azure-storage-blob")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def get_blob_service_client() -> BlobServiceClient:
    """Create Azure Blob Service client from environment variables."""
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

    if connection_string:
        return BlobServiceClient.from_connection_string(connection_string)

    account_name = os.environ.get("AZURE_STORAGE_ACCOUNT")
    account_key = os.environ.get("AZURE_STORAGE_KEY")

    if not account_name or not account_key:
        print("Error: Azure credentials not configured.")
        print("Set AZURE_STORAGE_CONNECTION_STRING or both AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY")
        sys.exit(1)

    account_url = f"https://{account_name}.blob.core.windows.net"
    return BlobServiceClient(account_url=account_url, credential=account_key)


def get_content_type(file_path: Path) -> str:
    """Get content type based on file extension."""
    content_types = {
        ".csv": "text/csv",
        ".parquet": "application/octet-stream",
        ".json": "application/json",
        ".duckdb": "application/octet-stream",
        ".log": "text/plain",
    }
    return content_types.get(file_path.suffix.lower(), "application/octet-stream")


def upload_file(blob_service: BlobServiceClient, local_path: Path,
                container: str, blob_name: str = None, overwrite: bool = True) -> bool:
    """Upload a single file to Azure Blob Storage."""
    if not local_path.exists():
        print(f"  Error: File not found: {local_path}")
        return False

    if blob_name is None:
        blob_name = local_path.name

    container_client = blob_service.get_container_client(container)
    blob_client = container_client.get_blob_client(blob_name)

    file_size = local_path.stat().st_size
    size_str = f"{file_size:,} bytes" if file_size < 1024 else f"{file_size/1024:.1f} KB"

    print(f"  Uploading: {local_path.name} ({size_str})")
    print(f"    -> {container}/{blob_name}")

    try:
        content_settings = ContentSettings(content_type=get_content_type(local_path))

        with open(local_path, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=overwrite,
                content_settings=content_settings
            )

        print(f"    Success")
        return True

    except Exception as e:
        print(f"    Error: {e}")
        return False


def upload_raw_files(blob_service: BlobServiceClient, base_path: Path) -> dict:
    """Upload all raw data files to the 'raw' container."""
    results = {"success": 0, "failed": 0}
    raw_path = base_path / "data" / "raw"

    print("\nUploading raw data files to 'raw' container...")

    if not raw_path.exists():
        print(f"  Warning: Raw data directory not found: {raw_path}")
        return results

    # Upload CSV, Parquet, and JSON files
    patterns = ["*.csv", "*.parquet", "*.json"]

    for pattern in patterns:
        for file_path in raw_path.glob(pattern):
            if upload_file(blob_service, file_path, "raw"):
                results["success"] += 1
            else:
                results["failed"] += 1

    return results


def upload_duckdb(blob_service: BlobServiceClient, base_path: Path) -> bool:
    """Upload DuckDB database to the 'duckdb' container."""
    db_path = base_path / "data" / "processed" / "vibe.duckdb"

    print("\nUploading DuckDB database to 'duckdb' container...")

    if not db_path.exists():
        print(f"  Warning: Database not found: {db_path}")
        return False

    return upload_file(blob_service, db_path, "duckdb", "vibe.duckdb")


def upload_logs(blob_service: BlobServiceClient, base_path: Path) -> dict:
    """Upload log files to the 'logs' container."""
    results = {"success": 0, "failed": 0}
    logs_path = base_path / "logs"

    print("\nUploading log files to 'logs' container...")

    if not logs_path.exists():
        print(f"  Warning: Logs directory not found: {logs_path}")
        return results

    for file_path in logs_path.glob("*.log"):
        # Add timestamp to log file name to preserve history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"

        if upload_file(blob_service, file_path, "logs", blob_name):
            results["success"] += 1
        else:
            results["failed"] += 1

    return results


def list_blobs(blob_service: BlobServiceClient, container: str = None) -> None:
    """List blobs in Azure containers."""
    containers = [container] if container else ["raw", "duckdb", "logs"]

    print("\nAzure Blob Storage Contents:")
    print("=" * 60)

    for container_name in containers:
        try:
            container_client = blob_service.get_container_client(container_name)
            blobs = list(container_client.list_blobs())

            print(f"\n{container_name}/ ({len(blobs)} files)")
            print("-" * 40)

            if blobs:
                for blob in blobs:
                    size = blob.size
                    size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                    modified = blob.last_modified.strftime("%Y-%m-%d %H:%M") if blob.last_modified else "N/A"
                    print(f"  {blob.name:<30} {size_str:>12}  {modified}")
            else:
                print("  (empty)")

        except Exception as e:
            print(f"\n{container_name}/")
            print(f"  Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Upload data to Azure Blob Storage")
    parser.add_argument("--all", action="store_true", help="Upload all data (raw + db + logs)")
    parser.add_argument("--raw", action="store_true", help="Upload raw data files only")
    parser.add_argument("--db", action="store_true", help="Upload DuckDB database only")
    parser.add_argument("--logs", action="store_true", help="Upload log files only")
    parser.add_argument("--file", help="Upload specific file to raw container")
    parser.add_argument("--list", action="store_true", help="List files in Azure")
    parser.add_argument("--container", help="Container for --list (default: all)")
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent

    try:
        blob_service = get_blob_service_client()
        account_name = os.environ.get("AZURE_STORAGE_ACCOUNT", "connected")
        print(f"Connected to Azure Storage: {account_name}")
    except Exception as e:
        print(f"Error connecting to Azure: {e}")
        sys.exit(1)

    if args.list:
        list_blobs(blob_service, args.container)
        return

    if args.file:
        file_path = base_path / "data" / "raw" / args.file
        if not file_path.exists():
            file_path = Path(args.file)
        print(f"\nUploading single file...")
        upload_file(blob_service, file_path, "raw")
        return

    # Track overall results
    total_success = 0
    total_failed = 0

    if args.all or args.raw or (not args.db and not args.logs):
        results = upload_raw_files(blob_service, base_path)
        total_success += results["success"]
        total_failed += results["failed"]

    if args.all or args.db:
        if upload_duckdb(blob_service, base_path):
            total_success += 1
        else:
            total_failed += 1

    if args.all or args.logs:
        results = upload_logs(blob_service, base_path)
        total_success += results["success"]
        total_failed += results["failed"]

    print(f"\n{'=' * 50}")
    print(f"Upload Complete: {total_success} succeeded, {total_failed} failed")

    if total_success > 0:
        print(f"\nVerify with: python scripts/upload_to_azure.py --list")


if __name__ == "__main__":
    main()
