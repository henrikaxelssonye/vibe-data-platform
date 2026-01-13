{% macro configure_azure_httpfs() %}
{#
    Configure DuckDB httpfs extension for Azure Blob Storage access.

    This macro should be called at the start of models that need to read
    from Azure Blob Storage URLs directly.

    Environment variables required:
    - AZURE_STORAGE_CONNECTION_STRING (preferred)
    - Or: AZURE_STORAGE_ACCOUNT + AZURE_STORAGE_KEY

    Usage in models:
        {{ configure_azure_httpfs() }}
        SELECT * FROM read_parquet('azure://account.blob.core.windows.net/container/file.parquet')
#}

{% if target.name == 'azure' %}
    {% set connection_string = env_var('AZURE_STORAGE_CONNECTION_STRING', '') %}
    {% set account_name = env_var('AZURE_STORAGE_ACCOUNT', '') %}
    {% set account_key = env_var('AZURE_STORAGE_KEY', '') %}

    {% if connection_string %}
        {% set configure_sql %}
            INSTALL azure;
            LOAD azure;
            INSTALL httpfs;
            LOAD httpfs;
            SET azure_storage_connection_string = '{{ connection_string }}';
        {% endset %}
        {% do run_query(configure_sql) %}
        {{ log("Azure httpfs configured with connection string", info=True) }}
    {% elif account_name and account_key %}
        {% set configure_sql %}
            INSTALL azure;
            LOAD azure;
            INSTALL httpfs;
            LOAD httpfs;
            SET azure_account_name = '{{ account_name }}';
            SET azure_account_key = '{{ account_key }}';
        {% endset %}
        {% do run_query(configure_sql) %}
        {{ log("Azure httpfs configured with account credentials", info=True) }}
    {% else %}
        {{ log("Warning: Azure credentials not found in environment", info=True) }}
    {% endif %}
{% else %}
    {{ log("Skipping Azure httpfs config (target: " ~ target.name ~ ")", info=True) }}
{% endif %}

{% endmacro %}


{% macro get_azure_blob_url(container, blob_name) %}
{#
    Generate an Azure Blob Storage URL for reading files.

    Args:
        container: Azure blob container name (e.g., 'raw')
        blob_name: Name of the blob file (e.g., 'customers.csv')

    Returns:
        Full Azure blob URL or local path depending on target

    Usage:
        SELECT * FROM read_csv_auto('{{ get_azure_blob_url("raw", "customers.csv") }}')
#}

{% set account_name = env_var('AZURE_STORAGE_ACCOUNT', '') %}

{% if target.name == 'azure' and account_name %}
    {{ return('azure://' ~ account_name ~ '.blob.core.windows.net/' ~ container ~ '/' ~ blob_name) }}
{% else %}
    {# Fall back to local path for dev target #}
    {{ return('../data/raw/' ~ blob_name) }}
{% endif %}

{% endmacro %}


{% macro read_azure_csv(container, blob_name) %}
{#
    Read a CSV file from Azure Blob Storage or local filesystem.
    Automatically handles target switching between local and cloud.

    Usage:
        SELECT * FROM {{ read_azure_csv('raw', 'customers.csv') }}
#}

{% set url = get_azure_blob_url(container, blob_name) %}
{{ return("read_csv_auto('" ~ url ~ "')") }}

{% endmacro %}


{% macro read_azure_parquet(container, blob_name) %}
{#
    Read a Parquet file from Azure Blob Storage or local filesystem.

    Usage:
        SELECT * FROM {{ read_azure_parquet('raw', 'data.parquet') }}
#}

{% set url = get_azure_blob_url(container, blob_name) %}
{{ return("read_parquet('" ~ url ~ "')") }}

{% endmacro %}


{% macro read_azure_json(container, blob_name) %}
{#
    Read a JSON file from Azure Blob Storage or local filesystem.

    Usage:
        SELECT * FROM {{ read_azure_json('raw', 'api_data.json') }}
#}

{% set url = get_azure_blob_url(container, blob_name) %}
{{ return("read_json_auto('" ~ url ~ "')") }}

{% endmacro %}
