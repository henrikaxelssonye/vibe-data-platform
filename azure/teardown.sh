#!/bin/bash
# Azure Infrastructure Teardown for Vibe Data Platform
#
# Usage: ./azure/teardown.sh [resource-group]
# Example: ./azure/teardown.sh vibe-data-platform-rg
#
# WARNING: This will permanently delete all resources in the resource group!

set -e

RESOURCE_GROUP="${1:-vibe-data-platform-rg}"
SERVICE_PRINCIPAL_NAME="vibe-data-platform-sp"

echo "=============================================="
echo "  Vibe Data Platform - Azure Teardown"
echo "=============================================="
echo ""
echo "WARNING: This will permanently delete:"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - All resources within the group (Storage Account, containers, data)"
echo "  - Service Principal: $SERVICE_PRINCIPAL_NAME"
echo ""

# Confirm deletion
read -p "Are you sure you want to proceed? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""

# Check Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    exit 1
fi

if ! az account show &> /dev/null; then
    echo "Error: Not logged into Azure. Run 'az login' first."
    exit 1
fi

# Delete Service Principal
echo "[1/2] Deleting Service Principal..."
SP_ID=$(az ad sp list --display-name "$SERVICE_PRINCIPAL_NAME" --query '[0].appId' -o tsv 2>/dev/null || true)
if [ -n "$SP_ID" ]; then
    az ad sp delete --id "$SP_ID" --output none
    echo "  Deleted: $SERVICE_PRINCIPAL_NAME"
else
    echo "  Service Principal not found (already deleted or never created)"
fi

# Delete Resource Group (includes all resources)
echo "[2/2] Deleting Resource Group..."
if az group exists --name "$RESOURCE_GROUP" | grep -q true; then
    az group delete \
        --name "$RESOURCE_GROUP" \
        --yes \
        --no-wait
    echo "  Deletion initiated: $RESOURCE_GROUP"
    echo "  (Resource group deletion happens asynchronously)"
else
    echo "  Resource Group not found (already deleted or never created)"
fi

echo ""
echo "=============================================="
echo "  Teardown Complete"
echo "=============================================="
echo ""
echo "Note: Resource group deletion may take a few minutes to complete."
echo "Check status with: az group exists --name $RESOURCE_GROUP"
echo ""
echo "Don't forget to:"
echo "  1. Remove GitHub Secrets if no longer needed"
echo "  2. Delete local .env file with Azure credentials"
echo ""
