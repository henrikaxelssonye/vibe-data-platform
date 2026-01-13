-- Staging model: standardize customer data
with source as (
    select * from {{ source('raw', 'raw_customers') }}
),

staged as (
    select
        customer_id,
        customer_name,
        lower(email) as email,
        city,
        country,
        cast(created_at as date) as created_at,
        current_timestamp as loaded_at
    from source
)

select * from staged
