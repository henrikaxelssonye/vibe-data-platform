-- Staging model: flatten daily weather forecast from Open-Meteo API
-- Source: api_weather_forecast.json
with raw_data as (
    select * from read_json_auto('../data/raw/api_weather_forecast.json')
),

metadata as (
    select
        extracted_at,
        data.latitude as latitude,
        data.longitude as longitude,
        data.timezone as timezone,
        data.elevation as elevation_m,
        data.daily.time as daily_times,
        data.daily.temperature_2m_max as daily_temp_max,
        data.daily.temperature_2m_min as daily_temp_min,
        data.daily.precipitation_sum as daily_precip,
        data.daily.wind_speed_10m_max as daily_wind_max
    from raw_data
),

-- Unnest daily arrays using generate_subscripts
daily_forecast as (
    select
        extracted_at,
        latitude,
        longitude,
        timezone,
        elevation_m,
        unnest(daily_times) as forecast_date,
        unnest(daily_temp_max) as temperature_max_c,
        unnest(daily_temp_min) as temperature_min_c,
        unnest(daily_precip) as precipitation_mm,
        unnest(daily_wind_max) as wind_speed_max_kmh
    from metadata
),

staged as (
    select
        cast(forecast_date as date) as forecast_date,
        latitude,
        longitude,
        timezone,
        elevation_m,
        temperature_max_c,
        temperature_min_c,
        round((temperature_max_c + temperature_min_c) / 2, 1) as temperature_avg_c,
        precipitation_mm,
        wind_speed_max_kmh,
        -- Weather classification
        case
            when precipitation_mm > 10 then 'heavy_precipitation'
            when precipitation_mm > 2 then 'moderate_precipitation'
            when precipitation_mm > 0 then 'light_precipitation'
            else 'dry'
        end as precipitation_category,
        case
            when temperature_max_c < 0 then 'freezing'
            when temperature_max_c < 10 then 'cold'
            when temperature_max_c < 20 then 'mild'
            when temperature_max_c < 30 then 'warm'
            else 'hot'
        end as temperature_category,
        extracted_at,
        current_timestamp as loaded_at
    from daily_forecast
)

select * from staged
