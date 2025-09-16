# Sensor Datapoint Access Feature

This feature provides a simple GraphQL API for accessing single sensor datapoints before, after, or interpolated at a given datetime.

## GraphQL Query

```graphql
query GetSensorDatapoint($sensorId: String!, $targetTime: DateTime!, $direction: String = "before") {
  sensorDatapoint(sensorId: $sensorId, targetTime: $targetTime, direction: $direction) {
    value
    timestamp
    isInterpolated
    sourceReadings {
      timestamp
      value
    }
  }
}
```

## Parameters

- `sensorId`: ID of the sensor
- `targetTime`: Target datetime in ISO format
- `direction`: One of:
  - `"before"` - Returns the last reading before the target time
  - `"after"` - Returns the first reading after the target time  
  - `"interpolate"` - Returns a linearly interpolated value at the target time

## Response

- `value`: The sensor value (float)
- `timestamp`: Timestamp of the reading (or target time for interpolated values)
- `isInterpolated`: Boolean indicating if the value was interpolated
- `sourceReadings`: Array of readings used to calculate the result

## Examples

### Get Last Reading Before a Time
```graphql
{
  sensorDatapoint(
    sensorId: "sensor-123"
    targetTime: "2024-01-15T12:00:00Z"
    direction: "before"
  ) {
    value
    timestamp
    isInterpolated
  }
}
```

### Get First Reading After a Time
```graphql
{
  sensorDatapoint(
    sensorId: "sensor-123"
    targetTime: "2024-01-15T12:00:00Z"
    direction: "after"
  ) {
    value
    timestamp
    isInterpolated
  }
}
```

### Get Interpolated Value at Exact Time
```graphql
{
  sensorDatapoint(
    sensorId: "sensor-123"
    targetTime: "2024-01-15T12:00:00Z"
    direction: "interpolate"
  ) {
    value
    timestamp
    isInterpolated
    sourceReadings {
      timestamp
      value
    }
  }
}
```

## Linear Interpolation

When using `direction: "interpolate"`, the system finds the closest readings before and after the target time and calculates a linearly interpolated value:

```
interpolated_value = before_value + factor * (after_value - before_value)
```

Where `factor` is the time distance ratio:
```
factor = (target_time - before_time) / (after_time - before_time)
```

If only one reading is available (before or after), it returns that reading without interpolation.

## Use Cases

- **Heat Pump Analysis**: Get precise energy consumption values at period boundaries
- **Historical Analysis**: Find sensor values at specific timestamps
- **Data Smoothing**: Interpolate missing values in time series data
- **Threshold Monitoring**: Check if sensor crossed a threshold at a specific time