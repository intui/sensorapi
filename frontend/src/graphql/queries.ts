import { gql } from '@apollo/client';

export const GET_SENSOR_TYPES = gql`
  query GetSensorTypes($activeOnly: Boolean = true) {
    sensorTypes(activeOnly: $activeOnly) {
      id
      name
      description
      unit
      dataType
      minValue
      maxValue
      isActive
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