-- Mart model: join customers with their order summary
with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('orders_summary') }}
),

customer_orders as (
    select
        c.customer_id,
        c.customer_name,
        c.email,
        c.city,
        c.country,
        c.created_at as customer_since,
        coalesce(o.total_orders, 0) as total_orders,
        coalesce(o.completed_orders, 0) as completed_orders,
        coalesce(o.total_revenue, 0) as total_revenue,
        o.first_order_date,
        o.last_order_date,
        case
            when o.total_orders is null then 'No Orders'
            when o.total_orders = 1 then 'New'
            when o.total_orders between 2 and 5 then 'Regular'
            else 'VIP'
        end as customer_segment,
        current_timestamp as updated_at
    from customers c
    left join orders o on c.customer_id = o.customer_id
)

select * from customer_orders
