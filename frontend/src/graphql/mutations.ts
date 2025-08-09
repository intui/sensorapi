import { gql } from '@apollo/client';

export const CREATE_SENSOR_TYPE = gql`
  mutation CreateSensorType($input: CreateSensorTypeInput!) {
    createSensorType(input: $input) {
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

export const CREATE_LOCATION = gql`
  mutation CreateLocation($input: CreateLocationInput!) {
    createLocation(input: $input) {
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

export const CREATE_SENSOR = gql`
  mutation CreateSensor($input: CreateSensorInput!) {
    createSensor(input: $input) {
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

export const CREATE_SENSOR_READING = gql`
  mutation CreateSensorReading($input: CreateSensorReadingInput!) {
    createSensorReading(input: $input) {
      id
      value
      rawValue
      timestamp
      receivedAt
      sensor {
        id
        name
      }
    }
  }
`;

export const DELETE_SENSOR_READINGS = gql`
  mutation DeleteSensorReadings($sensorId: String!) {
    deleteSensorReadings(sensorId: $sensorId)
  }
`;

// Update Mutations
export const UPDATE_SENSOR_TYPE = gql`
  mutation UpdateSensorType($id: String!, $input: UpdateSensorTypeInput!) {
    updateSensorType(id: $id, input: $input) {
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

export const UPDATE_LOCATION = gql`
  mutation UpdateLocation($id: String!, $input: UpdateLocationInput!) {
    updateLocation(id: $id, input: $input) {
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

export const UPDATE_SENSOR = gql`
  mutation UpdateSensor($id: String!, $input: UpdateSensorInput!) {
    updateSensor(id: $id, input: $input) {
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

export const UPDATE_SENSOR_READING = gql`
  mutation UpdateSensorReading($id: String!, $input: UpdateSensorReadingInput!) {
    updateSensorReading(id: $id, input: $input) {
      id
      value
      rawValue
      timestamp
      receivedAt
      sensor {
        id
        name
      }
    }
  }
`;

// Delete Mutations
export const DELETE_SENSOR_TYPE = gql`
  mutation DeleteSensorType($id: String!) {
    deleteSensorType(id: $id)
  }
`;

export const DELETE_LOCATION = gql`
  mutation DeleteLocation($id: String!) {
    deleteLocation(id: $id)
  }
`;

export const DELETE_SENSOR = gql`
  mutation DeleteSensor($id: String!) {
    deleteSensor(id: $id)
  }
`;

export const DELETE_SENSOR_READING = gql`
  mutation DeleteSensorReading($id: String!) {
    deleteSensorReading(id: $id)
  }
`;