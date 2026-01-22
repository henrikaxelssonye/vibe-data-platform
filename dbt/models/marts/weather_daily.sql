-- Mart model: daily weather summary with additional analytics fields
{{ config(materialized='table') }}

with forecast as (
    select * from {{ ref('stg_weather_forecast') }}
),

weather_daily as (
    select
        forecast_date,
        latitude,
        longitude,
        timezone,
        elevation_m,

        -- Temperature metrics
        temperature_max_c,
        temperature_min_c,
        temperature_avg_c,
        temperature_max_c - temperature_min_c as temperature_range_c,
        temperature_category,

        -- Precipitation metrics
        precipitation_mm,
        precipitation_category,
        case when precipitation_mm > 0 then true else false end as has_precipitation,

        -- Wind metrics
        wind_speed_max_kmh,
        case
            when wind_speed_max_kmh < 5 then 'calm'
            when wind_speed_max_kmh < 20 then 'light'
            when wind_speed_max_kmh < 40 then 'moderate'
            when wind_speed_max_kmh < 60 then 'strong'
            else 'very_strong'
        end as wind_category,

        -- Date dimensions for analytics
        extract(year from forecast_date) as year,
        extract(month from forecast_date) as month,
        extract(day from forecast_date) as day,
        extract(dow from forecast_date) as day_of_week,
        case
            when extract(dow from forecast_date) in (0, 6) then true
            else false
        end as is_weekend,

        -- Overall weather score (simplified - lower is worse conditions)
        round(
            50
            + (temperature_avg_c * 1.5)  -- Prefer warmer temps
            - (precipitation_mm * 5)      -- Penalize precipitation
            - (wind_speed_max_kmh * 0.3)  -- Penalize wind
        , 1) as weather_comfort_score,

        -- Metadata
        extracted_at,
        current_timestamp as updated_at
    from forecast
)

select * from weather_daily
