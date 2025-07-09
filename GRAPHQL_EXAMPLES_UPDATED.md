# GraphQL Query Examples

This file contains example GraphQL queries and mutations for the Sensor API.
You can use these in the GraphQL Playground at http://localhost:8000/graphql

## Queries

### 1. Get All Sensor Types

```graphql
query GetSensorTypes {
  sensorTypes {
    id
    name
    description
    unit
    dataType
    minValue
    maxValue
    isActive
  }
}
```

### 2. Get All Locations

```graphql
query GetLocations {
  locations {
    id
    name
    description
    parentId
    address
    city
    country
    latitude
    longitude
  }
}
```

### 3. Get All Sensors with Details

```graphql
query GetSensors {
  sensors {
    id
    deviceId
    name
    description
    manufacturer
    model
    isActive
    isOnline
    lastSeen
    sensorType {
      name
      unit
    }
    location {
      name
    }
    latestReading {
      value
      timestamp
    }
  }
}
```

### 4. Get Sensors by Location

```graphql
query GetSensorsByLocation($locationId: String!) {
  sensors(locationId: $locationId) {
    id
    deviceId
    name
    sensorType {
      name
      unit
    }
    latestReading {
      value
      timestamp
    }
  }
}
```

### 5. Get Time Series Data for a Sensor

```graphql
query GetSensorReadings($sensorId: String!, $limit: Int = 100) {
  sensorReadings(sensorId: $sensorId, limit: $limit) {
    id
    value
    timestamp
  }
}
```

### 6. Get Latest Readings for All Sensors

```graphql
query GetLatestReadings {
  latestReadings {
    id
    value
    timestamp
    sensor {
      name
      deviceId
      sensorType {
        name
        unit
      }
      location {
        name
      }
    }
  }
}
```

### 7. Get Sensor with Specific Device ID

```graphql
query GetSensorByDeviceId($deviceId: String!) {
  sensorByDeviceId(deviceId: $deviceId) {
    id
    name
    description
    isOnline
    lastSeen
    sensorType {
      name
      unit
    }
    location {
      name
      address
    }
    latestReading {
      value
      timestamp
    }
  }
}
```

### 8. Get Temperature Sensors Only

```graphql
query GetTemperatureSensors($sensorTypeId: String!) {
  sensors(sensorTypeId: $sensorTypeId) {
    id
    deviceId
    name
    location {
      name
    }
    latestReading {
      value
      timestamp
    }
  }
}
```

### 9. Get Alerts

```graphql
query GetAlerts($limit: Int = 50) {
  alerts(limit: $limit) {
    id
    alertType
    severity
    title
    message
    status
    triggeredAt
    sensor {
      name
      deviceId
      location {
        name
      }
    }
  }
}
```

## Mutations

### 1. Create a New Sensor Type

```graphql
mutation CreateSensorType {
  createSensorType(input: {
    name: "CO2 Level"
    description: "Carbon dioxide concentration sensor"
    unit: "ppm"
    dataType: "float"
    minValue: 0.0
    maxValue: 5000.0
  }) {
    id
    name
    unit
  }
}
```

### 2. Create a New Location

```graphql
mutation CreateLocation {
  createLocation(input: {
    name: "Laboratory A"
    description: "Research laboratory on the 2nd floor"
    address: "456 Science Avenue"
    city: "Helsinki"
    country: "Finland"
    latitude: 60.1699
    longitude: 24.9384
  }) {
    id
    name
    address
  }
}
```

### 3. Create a New Sensor

```graphql
mutation CreateSensor($sensorTypeId: String!, $locationId: String!) {
  createSensor(input: {
    deviceId: "CO2001"
    name: "CO2 Sensor - Lab A"
    description: "Monitors CO2 levels in Laboratory A"
    sensorTypeId: $sensorTypeId
    locationId: $locationId
    manufacturer: "AirSense Corp"
    model: "AS-CO2-100"
    firmwareVersion: "v2.1.3"
    samplingInterval: 60
  }) {
    id
    deviceId
    name
    manufacturer
  }
}
```

### 4. Add a Sensor Reading

```graphql
mutation CreateSensorReading($sensorId: String!) {
  createSensorReading(input: {
    sensorId: $sensorId
    value: 23.5
  }) {
    id
    value
    timestamp
  }
}
```

## Query Variables Examples

When using queries with variables, you can provide them like this:

### For GetSensorsByLocation:
```json
{
  "locationId": "your-location-uuid-here"
}
```

### For GetSensorReadings:
```json
{
  "sensorId": "your-sensor-uuid-here",
  "limit": 50
}
```

### For GetSensorByDeviceId:
```json
{
  "deviceId": "TEMP001"
}
```

### For CreateSensor:
```json
{
  "sensorTypeId": "your-sensor-type-uuid-here",
  "locationId": "your-location-uuid-here"
}
```

## Advanced Queries

### Get Sensor Dashboard Data
```graphql
query GetDashboardData {
  sensors(activeOnly: true, onlineOnly: true) {
    id
    deviceId
    name
    sensorType {
      name
      unit
    }
    location {
      name
    }
    latestReading {
      value
      timestamp
    }
  }
  
  alerts(status: "active", limit: 10) {
    id
    severity
    title
    triggeredAt
    sensor {
      name
      location {
        name
      }
    }
  }
}
```

### Get Location Hierarchy with Sensors
```graphql
query GetLocationHierarchy {
  locations(activeOnly: true) {
    id
    name
    parentId
    sensors {
      id
      deviceId
      sensorType {
        name
      }
      isOnline
      latestReading {
        value
        timestamp
      }
    }
  }
}
```

## Tips for Using the API

1. **Use the GraphQL Playground**: Navigate to http://localhost:8000/graphql for an interactive query interface
2. **Explore the Schema**: Use the "Docs" panel in the playground to explore available fields
3. **Start Simple**: Begin with basic queries and gradually add more fields
4. **Use Variables**: For dynamic queries, use GraphQL variables instead of hardcoding values
5. **Monitor Performance**: Large datasets should use pagination (limit parameter)
6. **Time Filters**: Use `startTime` and `endTime` parameters for time-range queries
