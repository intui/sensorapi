# Sensor Data Analysis Skill

Expert guidance for querying, analyzing, and visualizing sensor data from the SensorAPI system.

## Database Connection Pattern

```python
import sys, os
sys.path.insert(0, os.path.abspath('..'))  # from notebooks/ dir

from app.database.database import get_db_session
from app.database.models import Sensor, SensorReading, SensorType, Location

session = get_db_session()
# ... queries ...
session.close()
```

The database connection is configured via `DATABASE_URL` in `.env`. PostgreSQL only (UUID columns).

## Sensor Inventory

| Sensor Name | Type | Typical Unit | ~Readings |
|---|---|---|---|
| `warmepumpe_Energie_sum` | Energy meter (cumulative) | kWh | 95K |
| `idm_aero_hp_warmemenge_gesamt` | Thermal energy total | kWh | 97K |
| `idm_aero_hp_warmemenge_heizen` | Thermal energy heating | kWh | 87K |
| `idm_aero_hp_warmemenge_warmwasser` | Thermal energy hot water | kWh | 8K |
| `idm_aero_hp_idm_aero_hp_warmemenge_abtauung` | Thermal energy defrost | kWh | 2K |
| `idm_aero_hp_aktuelle_leistungsaufnahme_warmepumpe` | Instantaneous power | W | 66K |
| `idm_aero_hp_momentanleistung` | Thermal power | W | 94K |
| `Photovoltaics Power` | PV generation | W | 93K |
| `Household power draw` | Total household | W | 435K |
| `wohnzimmer_temperature` | Room temperature | °C | 11K |
| `ug_kueche_temp` | Room temperature | °C | 15K |
| `ug_arbeitszimmer_Temperature` | Room temperature | °C | 150 |
| `ug_arbeitszimmer_Valve` | Valve position | % | 161 |
| `ug_arbeitszimmer_Setpoint` | Temperature setpoint | °C | 156 |

## Common Query Patterns

### Load a single sensor time series
```python
sensor = session.query(Sensor).filter(Sensor.name == 'sensor_name').first()
rows = (session.query(SensorReading.timestamp, SensorReading.value)
        .filter(SensorReading.sensor_id == sensor.id)
        .order_by(SensorReading.timestamp).all())
df = pd.DataFrame(rows, columns=['timestamp', 'value'])
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
df = df.set_index('timestamp')
```

### Cumulative meter → hourly consumption
```python
hourly = df.resample('1h').last().dropna()
hourly['delta'] = hourly['value'].diff().clip(lower=0)
```

### Power (W) → hourly energy (kWh)
```python
hourly = df.resample('1h').mean()
hourly['kwh'] = hourly['value'] / 1000  # avg W over 1h ≈ kWh
```

### Filter by date range
```python
from datetime import datetime
start = datetime(2025, 10, 1, tzinfo=timezone.utc)
end = datetime(2025, 12, 31, tzinfo=timezone.utc)
rows = (session.query(SensorReading.timestamp, SensorReading.value)
        .filter(SensorReading.sensor_id == sensor.id,
                SensorReading.timestamp >= start,
                SensorReading.timestamp <= end)
        .order_by(SensorReading.timestamp).all())
```

## Visualization Recipes (Plotly)

### Time series line chart
```python
fig = px.line(df, x=df.index, y='value', title='Sensor Reading Over Time')
fig.show()
```

### Heatmap (hour × day-of-week)
```python
pivot = df.pivot_table(values='value', index=df.index.hour, columns=df.index.dayofweek, aggfunc='mean')
fig = go.Figure(go.Heatmap(z=pivot.values, x=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
                           y=list(range(24)), colorscale='YlOrRd'))
```

### Dual-axis chart
```python
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(...), secondary_y=False)
fig.add_trace(go.Scatter(...), secondary_y=True)
```

## Data Quality Checks

- **Gaps**: `df.resample('1h').count()` — look for zeros
- **Outliers**: `df[df['value'] > df['value'].quantile(0.999)]`
- **Negative deltas in cumulative meters**: `df['delta'][df['delta'] < 0]` — meter resets
- **Timezone**: All timestamps are stored in UTC. Use `pd.to_datetime(..., utc=True)`

## Location

Home location: Bonn, Germany (latitude=50.7374, longitude=7.0982)

## Key Analysis Notebooks

1. `notebooks/01_data_exploration.ipynb` — Sensor inventory, data coverage, quality checks
2. `notebooks/02_weather_energy_correlation.ipynb` — Weather impact on energy use
3. `notebooks/03_heatpump_cop_analysis.ipynb` — Heat pump COP calculation and trends
4. `notebooks/04_prediction_model_dev.ipynb` — ML model training and evaluation
5. `notebooks/05_household_load_profiles.ipynb` — Consumption patterns and PV self-sufficiency
