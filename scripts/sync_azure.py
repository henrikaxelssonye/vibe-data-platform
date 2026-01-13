#!/usr/bin/env python3
"""
Azure Blob Storage Sync Utility for Vibe Data Platform

Bidirectional sync between local filesystem and Azure Blob Storage.
Useful for development (download from Azure) and deployment (upload to Azure).

Usage:
    python scripts/sync_azure.py --download          # Download all from Azure
    python scripts/sync_azure.py --upload            # Upload all to Azure
    python scripts/sync_azure.py --download --raw    # Download raw data only
    python scripts/sync_azure.py --download --db     # Download DuckDB only
    python scripts/sync_azure.py --status            # Compare local vs Azure

Environment Variables (or use .env file):
    AZURE_STORAGE_ACCOUNT       - Storage account name
    AZURE_STORAGE_KEY           - Storage account access key
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    print("Error: azure-storage-blob not installed.")
    print("Install with: pip install azure-storage-blob")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_blob_service_client() -> BlobServiceClient:
    """Create Azure Blob Service client from environment variables."""
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

    if connection_string:
        return BlobServiceClient.from_connection_string(connection_string)

    account_name = os.environ.get("AZURE_STORAGE_ACCOUNT")
    account_key = os.environ.get("AZURE_STORAGE_KEY")

    if not account_name or not account_key:
        print("Error: Azure credentials not configured.")
        sys.exit(1)

    account_url = f"https://{account_name}.blob.core.windows.net"
    return BlobServiceClient(account_url=account_url, credential=account_key)


def download_blob(blob_service: BlobServiceClient, container: str,
                  blob_name: str, local_path: Path, overwrite: bool = True) -> bool:
    """Download a single blob from Azure."""
    if local_path.exists() and not overwrite:
        print(f"  Skipped (exists): {local_path.name}")
        return True

    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        container_client = blob_service.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        # Get blob properties for size
        properties = blob_client.get_blob_properties()
        size = properties.size
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"

        print(f"  Downloading: {blob_name} ({size_str})")
        print(f"    -> {local_path}")

        with open(local_path, "wb") as f:
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())

        print(f"    Success")
        return True

    except Exception as e:
        print(f"  Error downloading {blob_name}: {e}")
        return False


def download_container(blob_service: BlobServiceClient, container: str,
                       local_dir: Path, pattern: str = None) -> dict:
    """Download all blobs from a container."""
    results = {"success": 0, "failed": 0, "skipped": 0}

    try:
        container_client = blob_service.get_container_client(container)
        blobs = list(container_client.list_blobs())

        if not blobs:
            print(f"  (container is empty)")
            return results

        for blob in blobs:
            # Skip if pattern specified and doesn't match
            if pattern and not blob.name.endswith(pattern):
                continue

            local_path = local_dir / blob.name

            if download_blob(blob_service, container, blob.name, local_path):
                results["success"] += 1
            else:
                results["failed"] += 1

    except Exception as e:
        print(f"  Error listing container: {e}")
        results["failed"] += 1

    return results


def download_all(blob_service: BlobServiceClient, base_path: Path,
                 include_raw: bool = True, include_db: bool = True) -> dict:
    """Download data from Azure to local filesystem."""
    total = {"success": 0, "failed": 0}

    if include_raw:
        print("\nDownloading raw data from 'raw' container...")
        raw_path = base_path / "data" / "raw"
        results = download_container(blob_service, "raw", raw_path)
        total["success"] += results["success"]
        total["failed"] += results["failed"]

    if include_db:
        print("\nDownloading DuckDB from 'duckdb' container...")
        db_path = base_path / "data" / "processed"
        if download_blob(blob_service, "duckdb", "vibe.duckdb", db_path / "vibe.duckdb"):
            total["success"] += 1
        else:
            total["failed"] += 1

    return total


def upload_file(blob_service: BlobServiceClient, local_path: Path,
                container: str, blob_name: str = None) -> bool:
    """Upload a file to Azure."""
    if not local_path.exists():
        print(f"  Error: File not found: {local_path}")
        return False

    if blob_name is None:
        blob_name = local_path.name

    try:
        container_client = blob_service.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)

        size = local_path.stat().st_size
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"

        print(f"  Uploading: {local_path.name} ({size_str})")
        print(f"    -> {container}/{blob_name}")

        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"    Success")
        return True

    except Exception as e:
        print(f"  Error uploading {local_path.name}: {e}")
        return False


def upload_all(blob_service: BlobServiceClient, base_path: Path,
               include_raw: bool = True, include_db: bool = True) -> dict:
    """Upload data from local filesystem to Azure."""
    total = {"success": 0, "failed": 0}

    if include_raw:
        print("\nUploading raw data to 'raw' container...")
        raw_path = base_path / "data" / "raw"

        if raw_path.exists():
            for pattern in ["*.csv", "*.parquet", "*.json"]:
                for file_path in raw_path.glob(pattern):
                    if upload_file(blob_service, file_path, "raw"):
                        total["success"] += 1
                    else:
                        total["failed"] += 1
        else:
            print(f"  Warning: {raw_path} not found")

    if include_db:
        print("\nUploading DuckDB to 'duckdb' container...")
        db_path = base_path / "data" / "processed" / "vibe.duckdb"

        if db_path.exists():
            if upload_file(blob_service, db_path, "duckdb"):
                total["success"] += 1
            else:
                total["failed"] += 1
        else:
            print(f"  Warning: {db_path} not found")

    return total


def show_status(blob_service: BlobServiceClient, base_path: Path) -> None:
    """Compare local files with Azure blobs."""
    print("\nSync Status: Local vs Azure")
    print("=" * 70)

    # Check raw files
    print("\n[raw container]")
    raw_path = base_path / "data" / "raw"
    local_raw_files = set()

    if raw_path.exists():
        for pattern in ["*.csv", "*.parquet", "*.json"]:
            for f in raw_path.glob(pattern):
                local_raw_files.add(f.name)

    try:
        container_client = blob_service.get_container_client("raw")
        azure_raw_files = {blob.name for blob in container_client.list_blobs()}
    except Exception:
        azure_raw_files = set()

    only_local = local_raw_files - azure_raw_files
    only_azure = azure_raw_files - local_raw_files
    both = local_raw_files & azure_raw_files

    print(f"  In sync:      {len(both)} files")
    print(f"  Local only:   {len(only_local)} files {list(only_local) if only_local else ''}")
    print(f"  Azure only:   {len(only_azure)} files {list(only_azure) if only_azure else ''}")

    # Check DuckDB
    print("\n[duckdb container]")
    db_path = base_path / "data" / "processed" / "vibe.duckdb"
    local_db_exists = db_path.exists()

    try:
        container_client = blob_service.get_container_client("duckdb")
        azure_db_exists = any(blob.name == "vibe.duckdb" for blob in container_client.list_blobs())
    except Exception:
        azure_db_exists = False

    if local_db_exists and azure_db_exists:
        # Compare sizes
        local_size = db_path.stat().st_size
        try:
            blob_client = blob_service.get_blob_client("duckdb", "vibe.duckdb")
            azure_size = blob_client.get_blob_properties().size
            status = "MATCH" if local_size == azure_size else f"DIFFER (local: {local_size}, azure: {azure_size})"
        except Exception:
            status = "local exists"
        print(f"  vibe.duckdb: {status}")
    elif local_db_exists:
        print(f"  vibe.duckdb: LOCAL ONLY")
    elif azure_db_exists:
        print(f"  vibe.duckdb: AZURE ONLY")
    else:
        print(f"  vibe.duckdb: NOT FOUND")

    print("\n" + "=" * 70)
    print("Use --download to get Azure data locally")
    print("Use --upload to push local data to Azure")


def main():
    parser = argparse.ArgumentParser(description="Sync data with Azure Blob Storage")
    parser.add_argument("--download", action="store_true", help="Download from Azure to local")
    parser.add_argument("--upload", action="store_true", help="Upload from local to Azure")
    parser.add_argument("--status", action="store_true", help="Compare local vs Azure")
    parser.add_argument("--raw", action="store_true", help="Only sync raw data files")
    parser.add_argument("--db", action="store_true", help="Only sync DuckDB database")
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent

    try:
        blob_service = get_blob_service_client()
        print(f"Connected to Azure Storage")
    except Exception as e:
        print(f"Error connecting to Azure: {e}")
        sys.exit(1)

    # Determine what to sync
    include_raw = args.raw or (not args.raw and not args.db)
    include_db = args.db or (not args.raw and not args.db)

    if args.status or (not args.download and not args.upload):
        show_status(blob_service, base_path)
        return

    if args.download:
        results = download_all(blob_service, base_path, include_raw, include_db)
        print(f"\n{'=' * 50}")
        print(f"Download Complete: {results['success']} succeeded, {results['failed']} failed")

    if args.upload:
        results = upload_all(blob_service, base_path, include_raw, include_db)
        print(f"\n{'=' * 50}")
        print(f"Upload Complete: {results['success']} succeeded, {results['failed']} failed")


if __name__ == "__main__":
    main()
