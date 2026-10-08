import requests
import streamlit as st
import pandas as pd
import joblib
from auth import login_page, logout

st.set_page_config(
    page_title="AQPredict",
    page_icon="🌍",
    layout="wide"
)
st.image("logo.png", width=650)
# -----------------------------
# Login / Signup
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_page()
    st.stop()

# -----------------------------
# Logged-in user
# -----------------------------

st.image("logo.png", width=650)

st.title("🌍 AQPredict")
st.subheader("AI-Based Air Quality Prediction System")

st.write(
    f"Welcome, **{st.session_state['identifier']}** 👋"
)

logout()

# Load trained AI model
model = joblib.load("model.pkl")

# Location input
location = st.text_input("📍 Enter City")

if location:

    # -----------------------------
    # Find city coordinates
    # -----------------------------
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(geo_url, params=geo_params)
    geo_data = geo_response.json()

    if "results" not in geo_data:
        st.error("Location not found. Please enter a valid city.")
        st.stop()

    latitude = geo_data["results"][0]["latitude"]
    longitude = geo_data["results"][0]["longitude"]

    # -----------------------------
    # 5-Day Air Quality Forecast
    # -----------------------------
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    air_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,ozone",
        "forecast_days": 5,
        "timezone": "auto"
    }

    air_response = requests.get(air_url, params=air_params)
    air_data = air_response.json()

    air_df = pd.DataFrame(air_data["hourly"])

    # -----------------------------
    # 5-Day Weather Forecast
    # -----------------------------
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "forecast_days": 5,
        "timezone": "auto"
    }

    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()

    weather_df = pd.DataFrame(weather_data["hourly"])

    weather_df = weather_df.rename(columns={
        "temperature_2m": "temperature",
        "relative_humidity_2m": "humidity",
        "wind_speed_10m": "wind_speed"
    })

    # -----------------------------
    # Combine data
    # -----------------------------
    forecast_df = pd.merge(
        air_df,
        weather_df,
        on="time",
        how="inner"
    )

    forecast_df["date"] = pd.to_datetime(
        forecast_df["time"]
    ).dt.date

    # -----------------------------
    # Daily averages
    # -----------------------------
    daily_df = forecast_df.groupby("date").agg({
        "pm2_5": "mean",
        "pm10": "mean",
        "carbon_monoxide": "mean",
        "nitrogen_dioxide": "mean",
        "ozone": "mean",
        "temperature": "mean",
        "humidity": "mean",
        "wind_speed": "mean"
    }).reset_index()

    # -----------------------------
    # AI Prediction
    # -----------------------------
    predictions = []

    for _, row in daily_df.iterrows():

        input_data = pd.DataFrame([{
            "pm2_5": row["pm2_5"],
            "pm10": row["pm10"],
            "carbon_monoxide": row["carbon_monoxide"],
            "nitrogen_dioxide": row["nitrogen_dioxide"],
            "ozone": row["ozone"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "wind_speed": row["wind_speed"]
        }])

        predicted_aqi = model.predict(input_data)[0]

        predictions.append(round(predicted_aqi))

    daily_df["Predicted AQI"] = predictions

    # -----------------------------
    # Date selection
    # -----------------------------
    st.write(f"### 📍 {location} — 5-Day AI Forecast")

    selected_date = st.selectbox(
        "📅 Select Forecast Date",
        daily_df["date"].tolist()
    )

    selected = daily_df[
        daily_df["date"] == selected_date
    ].iloc[0]

    # -----------------------------
    # AI AQI — Separate Section
    # -----------------------------
    st.write("### 🤖 AI-Predicted Air Quality")

    predicted_aqi = int(selected["Predicted AQI"])

    if predicted_aqi <= 50:
        status = "Good"
    elif predicted_aqi <= 100:
        status = "Moderate"
    elif predicted_aqi <= 150:
        status = "Unhealthy for Sensitive Groups"
    elif predicted_aqi <= 200:
        status = "Unhealthy"
    elif predicted_aqi <= 300:
        status = "Very Unhealthy"
    else:
        status = "Hazardous"

    st.metric(
        "Predicted AQI",
        predicted_aqi
    )

    st.write(f"**Status: {status}**")

    # -----------------------------
    # Air Quality
    # -----------------------------
    st.write("### 🌫️ Air Quality")

    a1, a2, a3, a4, a5 = st.columns(5)

    a1.metric("PM2.5", f"{selected['pm2_5']:.1f}")
    a2.metric("PM10", f"{selected['pm10']:.1f}")
    a3.metric("CO", f"{selected['carbon_monoxide']:.1f}")
    a4.metric("NO₂", f"{selected['nitrogen_dioxide']:.1f}")
    a5.metric("O₃", f"{selected['ozone']:.1f}")

    # -----------------------------
    # Weather
    # -----------------------------
    st.write("### 🌤️ Weather")

    w1, w2, w3 = st.columns(3)

    w1.metric(
        "Temperature",
        f"{selected['temperature']:.1f} °C"
    )

    w2.metric(
        "Humidity",
        f"{selected['humidity']:.0f} %"
    )

    w3.metric(
        "Wind Speed",
        f"{selected['wind_speed']:.1f} km/h"
    )

    # -----------------------------
    # 5-Day AI Prediction Table
    # -----------------------------
    st.write("### 📊 5-Day AI Predictions")

    display_df = daily_df[
        ["date", "Predicted AQI"]
    ].copy()

    display_df["Status"] = display_df["Predicted AQI"].apply(
        lambda x:
        "Good" if x <= 50 else
        "Moderate" if x <= 100 else
        "Unhealthy for Sensitive Groups" if x <= 150 else
        "Unhealthy" if x <= 200 else
        "Very Unhealthy" if x <= 300 else
        "Hazardous"
    )

    st.dataframe(
        display_df,
        use_container_width=True
    )