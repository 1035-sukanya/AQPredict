import requests
import pandas as pd

latitude = 13.0827
longitude = 80.2707

# Air Quality API
air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

air_params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,ozone",
    "past_days": 92,
    "timezone": "auto"
}

air_response = requests.get(air_url, params=air_params)
air_data = air_response.json()

air_df = pd.DataFrame(air_data["hourly"])

# Weather API
weather_url = "https://api.open-meteo.com/v1/forecast"

weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    "past_days": 92,
    "timezone": "auto"
}

weather_response = requests.get(weather_url, params=weather_params)
weather_data = weather_response.json()

weather_df = pd.DataFrame(weather_data["hourly"])

# Combine air quality + weather data
df = pd.merge(
    air_df,
    weather_df,
    on="time",
    how="inner"
)

# Rename weather columns
df = df.rename(columns={
    "temperature_2m": "temperature",
    "relative_humidity_2m": "humidity",
    "wind_speed_10m": "wind_speed"
})

# Save complete historical dataset
df.to_csv("historical_air_quality.csv", index=False)

print("Historical air-quality + weather data downloaded successfully!")
print(f"Rows: {len(df)}")
print("Saved as historical_air_quality.csv")
print("Columns:")
print(df.columns.tolist())