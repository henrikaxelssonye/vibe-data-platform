-- Staging model: standardize product data
with source as (
    select * from {{ source('raw', 'raw_products') }}
),

staged as (
    select
        product_id,
        product_name,
        category,
        unit_price,
        cost_price,
        unit_price - cost_price as margin,
        round((unit_price - cost_price) / unit_price * 100, 2) as margin_pct,
        supplier,
        current_timestamp as loaded_at
    from source
)

select * from staged
