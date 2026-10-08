import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load historical data
data = pd.read_csv("historical_air_quality.csv")

# Create AQI target from PM2.5
data["AQI"] = data["pm2_5"] * 4.1667

# Remove missing values
data = data.dropna()

# Features
X = data[
    [
        "pm2_5",
        "pm10",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "ozone",
        "temperature",
        "humidity",
        "wind_speed"
    ]
]

# Target
y = data["AQI"]

# Random Forest AI model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("AI model trained successfully!")
print(f"Training rows: {len(data)}")
print("Model saved as model.pkl")