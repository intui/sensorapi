# Energy Prediction Skill

Expert guidance for building, training, and deploying energy consumption prediction models using weather forecast data.

## Architecture Overview

The prediction pipeline has three layers:
1. **Weather Service** (`app/services/weather.py`) — Fetches forecast/historical data from Open-Meteo
2. **Prediction Service** (`app/services/prediction.py`) — Trains and runs ML models
3. **GraphQL API** (`app/graphql/resolvers.py`) — Exposes predictions via queries/mutations

## Open-Meteo Weather API

Free API, no key required. Two endpoints:

### Forecast (7 days ahead)
```python
import httpx

params = {
    'latitude': 50.7374, 'longitude': 7.0982,  # Bonn
    'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,cloud_cover,direct_radiation',
    'forecast_days': 7,
    'timezone': 'Europe/Berlin'
}
async with httpx.AsyncClient() as client:
    r = await client.get('https://api.open-meteo.com/v1/forecast', params=params)
    data = r.json()
```

### Historical Archive
```python
params = {
    'latitude': 50.7374, 'longitude': 7.0982,
    'start_date': '2025-07-01', 'end_date': '2026-03-01',
    'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,cloud_cover,direct_radiation',
    'timezone': 'Europe/Berlin'
}
async with httpx.AsyncClient(timeout=60) as client:
    r = await client.get('https://archive-api.open-meteo.com/v1/archive', params=params)
```

### Available Variables
- `temperature_2m` — Air temperature at 2m (°C)
- `relative_humidity_2m` — Relative humidity (%)
- `wind_speed_10m` — Wind speed at 10m (km/h)
- `cloud_cover` — Total cloud cover (%)
- `direct_radiation` — Direct solar radiation (W/m²)
- `precipitation` — Precipitation (mm)

## Feature Engineering

### Core features (8 weather + time)
```python
features = {
    'temperature': weather['temperature_2m'],
    'humidity': weather['relative_humidity_2m'],
    'wind_speed': weather['wind_speed_10m'],
    'cloud_cover': weather['cloud_cover'],
    'solar_radiation': weather['direct_radiation'],
    'hour_sin': np.sin(2 * np.pi * hour / 24),
    'hour_cos': np.cos(2 * np.pi * hour / 24),
    'dow_sin': np.sin(2 * np.pi * dow / 7),
    'dow_cos': np.cos(2 * np.pi * dow / 7),
}
```

### Extended features (for higher accuracy)
```python
# Polynomial & interaction terms
'temperature_sq': temperature ** 2,
'temp_x_wind': temperature * wind_speed,
'temp_x_humidity': temperature * humidity,

# Lag features (previous consumption) — only for short-term predictions
'consumption_lag_1': consumption.shift(1),
'consumption_lag_2': consumption.shift(2),
'consumption_lag_3': consumption.shift(3),
```

## Model Training

### Recommended model: GradientBoostingRegressor
```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

model = GradientBoostingRegressor(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    random_state=42
)

# IMPORTANT: Use TimeSeriesSplit, not random splits
tscv = TimeSeriesSplit(n_splits=5)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
model.fit(X_scaled, y)
```

### Model evaluation metrics
- **MAE** (Mean Absolute Error) — primary metric, in kWh
- **R²** — explains variance captured by model
- **Residual analysis** — check for systematic bias

### Model persistence
```python
import joblib
joblib.dump(model, 'models/heatpump_gb_model.joblib')
joblib.dump(scaler, 'models/heatpump_scaler.joblib')
```

## GraphQL API Integration

### Query: Get energy predictions
```graphql
query {
  energyPredictions(
    sensorId: "uuid-here"
    horizonHours: 24
  ) {
    timestamp
    predictedValue
    confidenceLower
    confidenceUpper
    temperature
  }
}
```

### Query: Get weather forecast
```graphql
query {
  weatherForecast(locationId: "uuid-here", hours: 48) {
    timestamp
    temperature
    humidity
    windSpeed
    cloudCover
    solarRadiation
  }
}
```

### Mutation: Train/retrain model
```graphql
mutation {
  trainPredictionModel(input: {
    sensorId: "uuid-here"
    trainingDays: 90
  }) {
    success
    message
    metrics {
      mae
      r2
      sampleCount
    }
  }
}
```

## Prediction Horizons

| Horizon | Use Case | Feature Set |
|---|---|---|
| 24h | Next-day planning | Forecast weather + lag features |
| 96h | 4-day outlook | Forecast weather only (no lags) |
| 168h | Weekly planning | Forecast weather + seasonal patterns |

## Common Pitfalls

1. **Cumulative meters need delta computation** — Never predict raw cumulative values; compute hourly deltas first
2. **Timezone handling** — DB stores UTC, Open-Meteo returns local time. Always normalize to UTC
3. **Negative deltas** — Clip to zero; these represent meter resets, not negative consumption
4. **Lag features at forecast time** — For multi-step forecasts beyond a few hours, lag features are unavailable. Use weather-only model
5. **Seasonal bias** — Training on summer data won't predict winter well. Use at least 6 months of history
6. **Feature scaling** — GradientBoosting is tree-based and doesn't strictly need scaling, but StandardScaler helps with Ridge/Linear baselines

## File Locations

- Weather service: `app/services/weather.py`
- Prediction service: `app/services/prediction.py`
- GraphQL types: `app/graphql/types.py` (WeatherForecastPoint, PredictionResultType)
- GraphQL resolvers: `app/graphql/resolvers.py` (weather_forecast, energy_predictions queries)
- Frontend hook: `frontend/src/pages/HeatPump/hooks/usePrediction.tsx`
- Frontend components: `frontend/src/pages/HeatPump/components/PredictionChart.tsx`, `PredictionSummary.tsx`, `WeatherPreview.tsx`
- Model notebook: `notebooks/04_prediction_model_dev.ipynb`
