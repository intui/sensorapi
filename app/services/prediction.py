"""
Energy prediction service using scikit-learn.
Trains GradientBoosting models on historical energy + weather data to
predict future heat pump energy consumption from weather forecasts.
"""
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import joblib
import numpy as np

from app.services.weather import WeatherDataPoint, fetch_historical

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

MIN_TRAINING_SAMPLES = 48  # at least 48 hourly data points


@dataclass
class EnergyPredictionPoint:
    timestamp: str
    temperature: float
    predicted_electrical_kwh: float
    predicted_thermal_kwh: float
    predicted_cop: Optional[float]
    confidence_low_electrical: float
    confidence_high_electrical: float
    confidence_low_thermal: float
    confidence_high_thermal: float


@dataclass
class ModelInfo:
    r2_electrical: float
    r2_thermal: float
    training_samples: int
    trained_at: str
    feature_names: List[str] = field(default_factory=list)


@dataclass
class PredictionResult:
    predictions: List[EnergyPredictionPoint]
    total_electrical_kwh: float
    total_thermal_kwh: float
    average_cop: Optional[float]
    model_info: ModelInfo


def _model_path(electrical_sensor_id: str, thermal_sensor_id: str) -> Path:
    safe_e = electrical_sensor_id.replace("-", "")[:12]
    safe_t = thermal_sensor_id.replace("-", "")[:12]
    return MODELS_DIR / f"hp_{safe_e}_{safe_t}.joblib"


def _build_features(
    temperature: float,
    humidity: Optional[float],
    wind_speed: Optional[float],
    hour: int,
    day_of_week: int,
) -> np.ndarray:
    """Build feature vector for a single data point."""
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    dow_sin = np.sin(2 * np.pi * day_of_week / 7)
    dow_cos = np.cos(2 * np.pi * day_of_week / 7)
    return np.array([
        temperature,
        humidity if humidity is not None else 50.0,
        wind_speed if wind_speed is not None else 0.0,
        hour_sin,
        hour_cos,
        dow_sin,
        dow_cos,
        temperature ** 2,  # quadratic term for non-linear COP behaviour
    ])


FEATURE_NAMES = [
    "temperature", "humidity", "wind_speed",
    "hour_sin", "hour_cos", "dow_sin", "dow_cos",
    "temperature_sq",
]


def _pair_energy_with_weather(
    readings_electrical: List[dict],
    readings_thermal: List[dict],
    weather: List[WeatherDataPoint],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Pair energy readings with weather data by matching to the nearest hour.
    Energy readings are cumulative meter values – compute hourly deltas.

    Returns (X_features, y_electrical, y_thermal) arrays.
    """
    # Index weather by hour string
    weather_by_hour: dict[str, WeatherDataPoint] = {}
    for wp in weather:
        key = wp.timestamp[:13]  # "YYYY-MM-DDTHH"
        weather_by_hour[key] = wp

    # Build hourly energy deltas from cumulative readings
    def _hourly_deltas(readings: List[dict]) -> dict[str, float]:
        sorted_r = sorted(readings, key=lambda r: r["timestamp"])
        deltas: dict[str, float] = {}
        for i in range(1, len(sorted_r)):
            prev = sorted_r[i - 1]
            curr = sorted_r[i]
            ts_prev = prev["timestamp"]
            ts_curr = curr["timestamp"]
            # Only pair readings within ~2 hours of each other
            if isinstance(ts_prev, str):
                dt_prev = datetime.fromisoformat(ts_prev.replace("Z", "+00:00"))
            else:
                dt_prev = ts_prev
            if isinstance(ts_curr, str):
                dt_curr = datetime.fromisoformat(ts_curr.replace("Z", "+00:00"))
            else:
                dt_curr = ts_curr

            gap_hours = (dt_curr - dt_prev).total_seconds() / 3600
            if gap_hours < 0.5 or gap_hours > 2.0:
                continue

            delta = curr["value"] - prev["value"]
            if delta < 0:
                continue  # meter reset, skip

            hour_key = dt_curr.strftime("%Y-%m-%dT%H")
            deltas[hour_key] = delta
        return deltas

    elec_deltas = _hourly_deltas(readings_electrical)
    therm_deltas = _hourly_deltas(readings_thermal)

    # Build paired dataset
    X_list, y_e_list, y_t_list = [], [], []
    for hour_key in sorted(set(elec_deltas.keys()) & set(therm_deltas.keys()) & set(weather_by_hour.keys())):
        wp = weather_by_hour[hour_key]
        dt = datetime.fromisoformat(hour_key)
        features = _build_features(
            wp.temperature, wp.humidity, wp.wind_speed,
            dt.hour, dt.weekday(),
        )
        X_list.append(features)
        y_e_list.append(elec_deltas[hour_key])
        y_t_list.append(therm_deltas[hour_key])

    if not X_list:
        return np.array([]), np.array([]), np.array([])

    return np.array(X_list), np.array(y_e_list), np.array(y_t_list)


def train_model(
    readings_electrical: List[dict],
    readings_thermal: List[dict],
    latitude: float,
    longitude: float,
    electrical_sensor_id: str,
    thermal_sensor_id: str,
    lookback_days: int = 90,
) -> ModelInfo:
    """
    Train prediction models on historical data.

    Args:
        readings_electrical: List of {"timestamp": ..., "value": ...} dicts (cumulative kWh)
        readings_thermal: Same for thermal sensor
        latitude/longitude: For fetching historical weather
        electrical_sensor_id/thermal_sensor_id: For model file naming
        lookback_days: How many days of history to use

    Returns:
        ModelInfo with accuracy metrics
    """
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import cross_val_score

    # Determine date range from readings
    all_timestamps = []
    for r in readings_electrical + readings_thermal:
        ts = r["timestamp"]
        if isinstance(ts, str):
            all_timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
        else:
            all_timestamps.append(ts)

    if not all_timestamps:
        raise ValueError("No readings provided for training")

    end_dt = max(all_timestamps)
    start_dt = max(min(all_timestamps), end_dt - timedelta(days=lookback_days))

    # Fetch historical weather
    weather = fetch_historical(latitude, longitude, start_dt.date(), end_dt.date())
    if not weather:
        raise ValueError(f"No historical weather data available for ({latitude}, {longitude})")

    # Build training data
    X, y_e, y_t = _pair_energy_with_weather(readings_electrical, readings_thermal, weather)

    if len(X) < MIN_TRAINING_SAMPLES:
        raise ValueError(
            f"Not enough paired data points for training: {len(X)} found, "
            f"{MIN_TRAINING_SAMPLES} required. "
            f"Ensure sensors have overlapping hourly data within the lookback period."
        )

    # Train models
    model_e = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, random_state=42,
    )
    model_t = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, random_state=42,
    )

    model_e.fit(X, y_e)
    model_t.fit(X, y_t)

    # Evaluate with cross-validation (if enough data)
    n_splits = min(5, max(2, len(X) // 20))
    r2_e = float(np.mean(cross_val_score(model_e, X, y_e, cv=n_splits, scoring="r2")))
    r2_t = float(np.mean(cross_val_score(model_t, X, y_t, cv=n_splits, scoring="r2")))

    # Compute residual std for confidence intervals
    pred_e = model_e.predict(X)
    pred_t = model_t.predict(X)
    std_e = float(np.std(y_e - pred_e))
    std_t = float(np.std(y_t - pred_t))

    # Save models
    model_path = _model_path(electrical_sensor_id, thermal_sensor_id)
    joblib.dump({
        "model_electrical": model_e,
        "model_thermal": model_t,
        "std_electrical": std_e,
        "std_thermal": std_t,
        "r2_electrical": r2_e,
        "r2_thermal": r2_t,
        "training_samples": len(X),
        "trained_at": datetime.utcnow().isoformat(),
        "feature_names": FEATURE_NAMES,
    }, model_path)

    logger.info(f"Model trained: {len(X)} samples, R²(e)={r2_e:.3f}, R²(t)={r2_t:.3f}")

    return ModelInfo(
        r2_electrical=r2_e,
        r2_thermal=r2_t,
        training_samples=len(X),
        trained_at=datetime.utcnow().isoformat(),
        feature_names=FEATURE_NAMES,
    )


def predict_energy(
    weather_forecast: List[WeatherDataPoint],
    electrical_sensor_id: str,
    thermal_sensor_id: str,
) -> PredictionResult:
    """
    Predict energy consumption from weather forecast using a trained model.

    Args:
        weather_forecast: List of hourly forecast weather data points
        electrical_sensor_id/thermal_sensor_id: To locate the trained model

    Returns:
        PredictionResult with hourly predictions and summary
    """
    model_path = _model_path(electrical_sensor_id, thermal_sensor_id)
    if not model_path.exists():
        raise FileNotFoundError(
            "No trained model found. Please train the model first by clicking 'Train Model'."
        )

    bundle = joblib.load(model_path)
    model_e = bundle["model_electrical"]
    model_t = bundle["model_thermal"]
    std_e = bundle["std_electrical"]
    std_t = bundle["std_thermal"]

    predictions: List[EnergyPredictionPoint] = []
    total_e, total_t = 0.0, 0.0

    for wp in weather_forecast:
        dt = datetime.fromisoformat(wp.timestamp)
        features = _build_features(
            wp.temperature, wp.humidity, wp.wind_speed,
            dt.hour, dt.weekday(),
        ).reshape(1, -1)

        pred_e = float(max(0.0, model_e.predict(features)[0]))
        pred_t = float(max(0.0, model_t.predict(features)[0]))
        cop = pred_t / pred_e if pred_e > 0.01 else None

        predictions.append(EnergyPredictionPoint(
            timestamp=wp.timestamp,
            temperature=wp.temperature,
            predicted_electrical_kwh=round(pred_e, 4),
            predicted_thermal_kwh=round(pred_t, 4),
            predicted_cop=round(cop, 2) if cop is not None else None,
            confidence_low_electrical=round(max(0.0, pred_e - 1.96 * std_e), 4),
            confidence_high_electrical=round(pred_e + 1.96 * std_e, 4),
            confidence_low_thermal=round(max(0.0, pred_t - 1.96 * std_t), 4),
            confidence_high_thermal=round(pred_t + 1.96 * std_t, 4),
        ))

        total_e += pred_e
        total_t += pred_t

    avg_cop = total_t / total_e if total_e > 0.01 else None

    return PredictionResult(
        predictions=predictions,
        total_electrical_kwh=round(total_e, 2),
        total_thermal_kwh=round(total_t, 2),
        average_cop=round(avg_cop, 2) if avg_cop is not None else None,
        model_info=ModelInfo(
            r2_electrical=bundle.get("r2_electrical", 0.0),
            r2_thermal=bundle.get("r2_thermal", 0.0),
            training_samples=bundle.get("training_samples", 0),
            trained_at=bundle.get("trained_at", ""),
            feature_names=bundle.get("feature_names", FEATURE_NAMES),
        ),
    )
