-- Mart model: aggregate order metrics by customer
with orders as (
    select * from {{ ref('stg_orders') }}
),

summary as (
    select
        customer_id,
        count(distinct order_id) as total_orders,
        sum(case when status = 'completed' then 1 else 0 end) as completed_orders,
        sum(case when status = 'pending' then 1 else 0 end) as pending_orders,
        sum(case when status = 'cancelled' then 1 else 0 end) as cancelled_orders,
        sum(case when status = 'completed' then line_total - discount_amount else 0 end) as total_revenue,
        sum(case when status = 'completed' then discount_amount else 0 end) as total_discounts,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        current_timestamp as updated_at
    from orders
    group by customer_id
)

select * from summary
