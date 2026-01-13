#!/usr/bin/env python3
"""
API Data Extraction Utility for Vibe Data Platform

This script extracts data from configured API sources and saves to local files.
Configuration is read from config/sources.yml.

Usage:
    python scripts/extract_api.py                    # Extract all enabled APIs
    python scripts/extract_api.py --source users    # Extract specific endpoint
    python scripts/extract_api.py --list            # List available sources
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml


def load_config() -> dict:
    """Load source configuration from config/sources.yml."""
    config_path = Path(__file__).parent.parent / "config" / "sources.yml"
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_auth_header(api_config: dict) -> dict:
    """Build authentication header based on config."""
    auth_type = api_config.get("auth_type", "none")

    if auth_type == "none":
        return {}

    if auth_type == "bearer":
        env_var = api_config.get("auth_env_var", "")
        token = os.environ.get(env_var, "")
        if not token:
            print(f"Warning: Environment variable {env_var} not set")
            return {}
        return {"Authorization": f"Bearer {token}"}

    if auth_type == "api_key":
        env_var = api_config.get("auth_env_var", "")
        api_key = os.environ.get(env_var, "")
        if not api_key:
            print(f"Warning: Environment variable {env_var} not set")
            return {}
        return {"X-API-Key": api_key}

    return {}


def extract_endpoint(api_name: str, api_config: dict, endpoint: dict) -> bool:
    """Extract data from a single API endpoint."""
    base_url = api_config["base_url"]
    url = f"{base_url}{endpoint['path']}"
    method = endpoint.get("method", "GET")
    output_file = Path(__file__).parent.parent / endpoint["output_file"]

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Extracting: {endpoint['name']}")
    print(f"    URL: {url}")

    try:
        headers = get_auth_header(api_config)
        headers["Accept"] = "application/json"

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, timeout=30)
        else:
            print(f"    Error: Unsupported method {method}")
            return False

        response.raise_for_status()
        data = response.json()

        # Add metadata
        result = {
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "source": api_name,
            "endpoint": endpoint["name"],
            "url": url,
            "record_count": len(data) if isinstance(data, list) else 1,
            "data": data
        }

        # Write to file
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

        record_count = len(data) if isinstance(data, list) else 1
        print(f"    Success: {record_count} records -> {output_file}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"    Error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"    Error: Invalid JSON response - {e}")
        return False


def extract_api(api_name: str, api_config: dict, endpoint_filter: str = None) -> dict:
    """Extract data from all endpoints of an API source."""
    print(f"\nExtracting from: {api_name}")
    print(f"  Base URL: {api_config['base_url']}")

    results = {"success": 0, "failed": 0}

    for endpoint in api_config.get("endpoints", []):
        if endpoint_filter and endpoint["name"] != endpoint_filter:
            continue

        if extract_endpoint(api_name, api_config, endpoint):
            results["success"] += 1
        else:
            results["failed"] += 1

    return results


def list_sources(config: dict) -> None:
    """List all configured API sources."""
    print("\nConfigured API Sources:")
    print("-" * 50)

    apis = config.get("sources", {}).get("apis", {})
    for name, api_config in apis.items():
        enabled = api_config.get("enabled", False)
        status = "ENABLED" if enabled else "DISABLED"
        print(f"\n  {name} [{status}]")
        print(f"    Base URL: {api_config.get('base_url', 'N/A')}")
        print(f"    Auth: {api_config.get('auth_type', 'none')}")
        print(f"    Endpoints:")
        for endpoint in api_config.get("endpoints", []):
            print(f"      - {endpoint['name']}: {endpoint['path']}")


def main():
    parser = argparse.ArgumentParser(description="Extract data from API sources")
    parser.add_argument("--source", help="Specific endpoint name to extract")
    parser.add_argument("--api", help="Specific API to extract from")
    parser.add_argument("--list", action="store_true", help="List available sources")
    parser.add_argument("--all", action="store_true", help="Extract from all enabled APIs")
    args = parser.parse_args()

    config = load_config()

    if args.list:
        list_sources(config)
        return

    apis = config.get("sources", {}).get("apis", {})
    total_success = 0
    total_failed = 0

    for api_name, api_config in apis.items():
        # Skip disabled APIs unless specifically requested
        if not api_config.get("enabled", False) and api_name != args.api:
            continue

        # Filter by API name if specified
        if args.api and api_name != args.api:
            continue

        results = extract_api(api_name, api_config, args.source)
        total_success += results["success"]
        total_failed += results["failed"]

    print(f"\n{'=' * 50}")
    print(f"Extraction Complete: {total_success} succeeded, {total_failed} failed")


if __name__ == "__main__":
    main()
