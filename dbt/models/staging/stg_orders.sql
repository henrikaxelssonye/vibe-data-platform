-- Staging model: clean and standardize raw order data
with source as (
    select * from {{ ref('sample_orders') }}
),

staged as (
    select
        order_id,
        customer_id,
        cast(order_date as date) as order_date,
        product_name,
        quantity,
        unit_price,
        quantity * unit_price as line_total,
        status,
        current_timestamp as loaded_at
    from source
)

select * from staged
