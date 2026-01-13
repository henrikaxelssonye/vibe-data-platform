#!/bin/bash
# Azure Infrastructure Setup for Vibe Data Platform
#
# Usage: ./azure/setup.sh [resource-group] [location]
# Example: ./azure/setup.sh vibe-data-platform-rg westeurope
#
# Prerequisites:
#   - Azure CLI installed and authenticated (az login)
#   - Subscription with permissions to create resources
#
# This script creates:
#   - Resource Group
#   - Storage Account with 3 containers (raw, duckdb, logs)
#   - Service Principal with Storage Blob Data Contributor role
#   - SAS token for blob access

set -e

# Configuration
RESOURCE_GROUP="${1:-vibe-data-platform-rg}"
LOCATION="${2:-westeurope}"
# Generate unique storage account name (must be lowercase, 3-24 chars, alphanumeric only)
STORAGE_ACCOUNT="vibedata$(date +%s | tail -c 8)"
SERVICE_PRINCIPAL_NAME="vibe-data-platform-sp"

echo "=============================================="
echo "  Vibe Data Platform - Azure Setup"
echo "=============================================="
echo ""
echo "Configuration:"
echo "  Resource Group:   $RESOURCE_GROUP"
echo "  Location:         $LOCATION"
echo "  Storage Account:  $STORAGE_ACCOUNT"
echo ""

# Check Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Install from https://aka.ms/installazurecli"
    exit 1
fi

if ! az account show &> /dev/null; then
    echo "Error: Not logged into Azure. Run 'az login' first."
    exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Using subscription: $SUBSCRIPTION_ID"
echo ""

# Create Resource Group
echo "[1/6] Creating Resource Group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none
echo "  Created: $RESOURCE_GROUP"

# Create Storage Account
echo "[2/6] Creating Storage Account..."
az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot \
    --allow-blob-public-access false \
    --output none
echo "  Created: $STORAGE_ACCOUNT"

# Get Storage Account Key
echo "[3/6] Retrieving Storage Account Key..."
STORAGE_KEY=$(az storage account keys list \
    --account-name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --query '[0].value' -o tsv)
echo "  Retrieved key successfully"

# Create Containers
echo "[4/6] Creating Blob Containers..."
for container in raw duckdb logs; do
    az storage container create \
        --name "$container" \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --output none
    echo "  Created container: $container"
done

# Create Service Principal
echo "[5/6] Creating Service Principal..."
# Check if SP already exists and delete it
EXISTING_SP=$(az ad sp list --display-name "$SERVICE_PRINCIPAL_NAME" --query '[0].appId' -o tsv 2>/dev/null || true)
if [ -n "$EXISTING_SP" ]; then
    echo "  Removing existing Service Principal..."
    az ad sp delete --id "$EXISTING_SP" --output none 2>/dev/null || true
fi

SP_JSON=$(az ad sp create-for-rbac \
    --name "$SERVICE_PRINCIPAL_NAME" \
    --role "Storage Blob Data Contributor" \
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
    --output json)
echo "  Created: $SERVICE_PRINCIPAL_NAME"

# Generate SAS Token (valid for 1 year)
echo "[6/6] Generating SAS Token..."
# Calculate expiry date (1 year from now)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    EXPIRY=$(date -v+1y '+%Y-%m-%dT%H:%MZ')
else
    # Linux/Windows Git Bash
    EXPIRY=$(date -u -d "1 year" '+%Y-%m-%dT%H:%MZ' 2>/dev/null || date -u '+%Y-%m-%dT%H:%MZ')
fi

SAS_TOKEN=$(az storage account generate-sas \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --services b \
    --resource-types sco \
    --permissions rwdlacup \
    --expiry "$EXPIRY" \
    --output tsv)
echo "  Generated SAS token (expires: $EXPIRY)"

# Build connection string
CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=$STORAGE_ACCOUNT;AccountKey=$STORAGE_KEY;EndpointSuffix=core.windows.net"

echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "=== Blob URLs ==="
echo "RAW_CONTAINER_URL=https://$STORAGE_ACCOUNT.blob.core.windows.net/raw"
echo "DUCKDB_CONTAINER_URL=https://$STORAGE_ACCOUNT.blob.core.windows.net/duckdb"
echo "LOGS_CONTAINER_URL=https://$STORAGE_ACCOUNT.blob.core.windows.net/logs"
echo ""
echo "=== GitHub Secrets to Configure ==="
echo "Add these secrets to your GitHub repository:"
echo "(Settings > Secrets and variables > Actions > New repository secret)"
echo ""
echo "AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT"
echo "AZURE_STORAGE_KEY=$STORAGE_KEY"
echo "AZURE_SAS_TOKEN=$SAS_TOKEN"
echo "AZURE_STORAGE_CONNECTION_STRING=$CONNECTION_STRING"
echo "AZURE_CREDENTIALS=$SP_JSON"
echo ""
echo "=== Local Development ==="
echo "Create a .env file with these values (do not commit to git):"
echo ""
echo "# Copy to .env file"
cat << EOF
AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT
AZURE_STORAGE_KEY=$STORAGE_KEY
AZURE_SAS_TOKEN=$SAS_TOKEN
AZURE_STORAGE_CONNECTION_STRING=$CONNECTION_STRING
EOF
echo ""
echo "=== Next Steps ==="
echo "1. Copy the GitHub secrets above to your repository"
echo "2. Run: python scripts/upload_to_azure.py --all"
echo "3. Test with: az storage blob list --container-name raw --account-name $STORAGE_ACCOUNT"
echo ""
