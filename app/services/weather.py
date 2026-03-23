"""
Weather service using Open-Meteo API (free, no API key required).
Provides both forecast and historical weather data.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional

import httpx

logger = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
REQUEST_TIMEOUT = 15.0


@dataclass
class WeatherDataPoint:
    timestamp: str
    temperature: float
    humidity: Optional[float]
    wind_speed: Optional[float]
    precipitation: Optional[float]
    cloud_cover: Optional[int]


def fetch_forecast(
    latitude: float,
    longitude: float,
    hours: int = 96,
) -> List[WeatherDataPoint]:
    """
    Fetch hourly weather forecast from Open-Meteo.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        hours: Number of forecast hours (max ~384 = 16 days)

    Returns:
        List of hourly weather data points
    """
    forecast_days = max(1, min((hours + 23) // 24, 16))

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,cloud_cover",
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()

    hourly = data.get("hourly", {})
    timestamps = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    wind_speeds = hourly.get("wind_speed_10m", [])
    precipitations = hourly.get("precipitation", [])
    cloud_covers = hourly.get("cloud_cover", [])

    points: List[WeatherDataPoint] = []
    for i in range(min(hours, len(timestamps))):
        points.append(WeatherDataPoint(
            timestamp=timestamps[i],
            temperature=temperatures[i] if i < len(temperatures) else 0.0,
            humidity=humidities[i] if i < len(humidities) else None,
            wind_speed=wind_speeds[i] if i < len(wind_speeds) else None,
            precipitation=precipitations[i] if i < len(precipitations) else None,
            cloud_cover=cloud_covers[i] if i < len(cloud_covers) else None,
        ))

    return points


def fetch_historical(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
) -> List[WeatherDataPoint]:
    """
    Fetch historical hourly weather data from Open-Meteo Archive API.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        start_date: Start date for historical data
        end_date: End date for historical data

    Returns:
        List of hourly historical weather data points
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,cloud_cover",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": "UTC",
    }

    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        response = client.get(HISTORICAL_URL, params=params)
        response.raise_for_status()
        data = response.json()

    hourly = data.get("hourly", {})
    timestamps = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    wind_speeds = hourly.get("wind_speed_10m", [])
    precipitations = hourly.get("precipitation", [])
    cloud_covers = hourly.get("cloud_cover", [])

    points: List[WeatherDataPoint] = []
    for i in range(len(timestamps)):
        temp = temperatures[i] if i < len(temperatures) else None
        if temp is None:
            continue
        points.append(WeatherDataPoint(
            timestamp=timestamps[i],
            temperature=temp,
            humidity=humidities[i] if i < len(humidities) else None,
            wind_speed=wind_speeds[i] if i < len(wind_speeds) else None,
            precipitation=precipitations[i] if i < len(precipitations) else None,
            cloud_cover=cloud_covers[i] if i < len(cloud_covers) else None,
        ))

    return points
