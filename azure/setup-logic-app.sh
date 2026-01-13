#!/bin/bash
# Azure Logic App Setup for Email Notifications
#
# Usage: ./azure/setup-logic-app.sh [resource-group] [location] [notification-email]
# Example: ./azure/setup-logic-app.sh vibe-data-platform-rg westeurope alerts@company.com
#
# Prerequisites:
#   - Azure CLI installed and authenticated
#   - Resource group already created (run setup.sh first)
#
# This script creates a Logic App with HTTP trigger that sends emails via SendGrid.
# Note: For production, you may want to use Office 365 connector instead.

set -e

RESOURCE_GROUP="${1:-vibe-data-platform-rg}"
LOCATION="${2:-westeurope}"
NOTIFICATION_EMAIL="${3:-}"
LOGIC_APP_NAME="vibe-data-notify"

echo "=============================================="
echo "  Vibe Data Platform - Logic App Setup"
echo "=============================================="
echo ""

if [ -z "$NOTIFICATION_EMAIL" ]; then
    read -p "Enter notification email address: " NOTIFICATION_EMAIL
fi

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location:       $LOCATION"
echo "  Logic App:      $LOGIC_APP_NAME"
echo "  Email:          $NOTIFICATION_EMAIL"
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    exit 1
fi

if ! az account show &> /dev/null; then
    echo "Error: Not logged into Azure. Run 'az login' first."
    exit 1
fi

# Check if resource group exists
if ! az group exists --name "$RESOURCE_GROUP" | grep -q true; then
    echo "Error: Resource group '$RESOURCE_GROUP' does not exist."
    echo "Run ./azure/setup.sh first to create the infrastructure."
    exit 1
fi

# Create Logic App workflow definition
# This is a simple HTTP-triggered workflow that logs the request
# For email, you'll need to configure a connector in the Azure Portal
WORKFLOW_DEFINITION=$(cat << 'EOF'
{
    "definition": {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "triggers": {
            "manual": {
                "type": "Request",
                "kind": "Http",
                "inputs": {
                    "method": "POST",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "subject": {
                                "type": "string"
                            },
                            "body": {
                                "type": "string"
                            },
                            "timestamp": {
                                "type": "string"
                            },
                            "run_id": {
                                "type": "string"
                            },
                            "repository": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        },
        "actions": {
            "Response": {
                "type": "Response",
                "kind": "Http",
                "inputs": {
                    "statusCode": 200,
                    "body": {
                        "status": "received",
                        "message": "Notification logged"
                    }
                },
                "runAfter": {}
            }
        },
        "outputs": {}
    }
}
EOF
)

echo "[1/2] Creating Logic App..."

# Create the Logic App
az logic workflow create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$LOGIC_APP_NAME" \
    --location "$LOCATION" \
    --definition "$WORKFLOW_DEFINITION" \
    --output none

echo "  Created: $LOGIC_APP_NAME"

echo "[2/2] Retrieving Webhook URL..."

# Get the callback URL for the HTTP trigger
# Note: This requires the workflow to be in 'Enabled' state
CALLBACK_URL=$(az logic workflow show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$LOGIC_APP_NAME" \
    --query "accessEndpoint" -o tsv)

# The actual trigger URL needs to be retrieved differently
# We need to get the trigger callback URL
TRIGGER_URL=$(az rest \
    --method POST \
    --uri "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Logic/workflows/$LOGIC_APP_NAME/triggers/manual/listCallbackUrl?api-version=2016-06-01" \
    --query "value" -o tsv 2>/dev/null || echo "")

if [ -z "$TRIGGER_URL" ]; then
    echo ""
    echo "Note: Could not auto-retrieve trigger URL."
    echo "Get it manually from Azure Portal:"
    echo "  1. Go to Logic Apps > $LOGIC_APP_NAME"
    echo "  2. Click 'Logic app designer'"
    echo "  3. Click on the HTTP trigger"
    echo "  4. Copy the 'HTTP POST URL'"
    TRIGGER_URL="<retrieve-from-azure-portal>"
fi

echo ""
echo "=============================================="
echo "  Logic App Setup Complete"
echo "=============================================="
echo ""
echo "=== GitHub Secret ==="
echo "Add this secret to your repository:"
echo ""
echo "LOGIC_APP_EMAIL_URL=$TRIGGER_URL"
echo ""
echo "=== Manual Configuration Required ==="
echo "To enable email sending:"
echo ""
echo "1. Go to Azure Portal > Logic Apps > $LOGIC_APP_NAME"
echo "2. Click 'Logic app designer'"
echo "3. Add a new action after the trigger:"
echo "   - Search for 'Send an email' (Office 365 or SendGrid)"
echo "   - Configure the connector with your email service"
echo "   - Use dynamic content from the trigger:"
echo "     - Subject: @{triggerBody()?['subject']}"
echo "     - Body: @{triggerBody()?['body']}"
echo "     - To: $NOTIFICATION_EMAIL"
echo "4. Save the Logic App"
echo ""
echo "=== Test the Webhook ==="
echo "curl -X POST '$TRIGGER_URL' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"subject\": \"Test\", \"body\": \"Hello from Vibe Data Platform\"}'"
echo ""
