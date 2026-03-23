import { gql } from '@apollo/client';

export const GET_SENSOR_TYPES = gql`
  query GetSensorTypes($activeOnly: Boolean = true) {
    sensorTypes(activeOnly: $activeOnly) {
      id
      name
      description
      unit
      minValue
      maxValue
      createdAt
    }
  }
`;

export const GET_LOCATIONS = gql`
  query GetLocations($activeOnly: Boolean = true) {
    locations(activeOnly: $activeOnly) {
      id
      name
      description
      city
      country
      postalCode
      address
      latitude
      longitude
      isActive
      createdAt
    }
  }
`;

export const GET_SENSORS = gql`
  query GetSensors($locationId: String, $sensorTypeId: String, $activeOnly: Boolean = true, $onlineOnly: Boolean = false) {
    sensors(locationId: $locationId, sensorTypeId: $sensorTypeId, activeOnly: $activeOnly, onlineOnly: $onlineOnly) {
      id
      deviceId
      name
      description
      manufacturer
      model
      firmwareVersion
      hardwareVersion
      samplingInterval
      isActive
      isOnline
      lastSeen
      createdAt
      sensorType {
        id
        name
        unit
      }
      location {
        id
        name
        city
      }
    }
  }
`;

export const GET_SENSOR_READINGS = gql`
  query GetSensorReadings($sensorId: String!, $limit: Int = 100, $offset: Int = 0, $startTime: DateTime, $endTime: DateTime) {
    sensorReadings(sensorId: $sensorId, limit: $limit, offset: $offset, startTime: $startTime, endTime: $endTime) {
      id
      value
      rawValue
      timestamp
      receivedAt
      sensor {
        id
        name
        sensorType {
          name
          unit
        }
      }
    }
  }
`;

export const GET_SENSOR_DATA_STATS = gql`
  query GetSensorDataStats($sensorId: String!) {
    sensorDataStats(sensorId: $sensorId) {
      firstReading {
        timestamp
        value
      }
      lastReading {
        timestamp
        value
      }
      totalCount
      dateRange {
        start
        end
      }
    }
  }
`;

export const GET_SENSOR_READINGS_AROUND = gql`
  query GetSensorReadingsAround($sensorId: String!, $targetTime: DateTime!, $before: Int = 1, $after: Int = 1) {
    sensorReadingsAround(sensorId: $sensorId, targetTime: $targetTime, before: $before, after: $after) {
      before {
        timestamp
        value
      }
      after {
        timestamp
        value
      }
    }
  }
`;

export const GET_WEATHER_FORECAST = gql`
  query GetWeatherForecast($locationId: String!, $hours: Int = 96) {
    weatherForecast(locationId: $locationId, hours: $hours) {
      timestamp
      temperature
      humidity
      windSpeed
      precipitation
      cloudCover
    }
  }
`;

export const GET_ENERGY_PREDICTIONS = gql`
  query GetEnergyPredictions($electricalSensorId: String!, $thermalSensorId: String!, $locationId: String!, $hours: Int = 96) {
    energyPredictions(electricalSensorId: $electricalSensorId, thermalSensorId: $thermalSensorId, locationId: $locationId, hours: $hours) {
      predictions {
        timestamp
        temperature
        predictedElectricalKwh
        predictedThermalKwh
        predictedCop
        confidenceLowElectrical
        confidenceHighElectrical
        confidenceLowThermal
        confidenceHighThermal
      }
      totalElectricalKwh
      totalThermalKwh
      averageCop
      modelInfo {
        r2Electrical
        r2Thermal
        trainingSamples
        trainedAt
        featureNames
      }
    }
  }
`;