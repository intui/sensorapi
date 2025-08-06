export interface SensorType {
  id: string;
  name: string;
  description?: string;
  unit?: string;
  dataType: string;
  minValue?: number;
  maxValue?: number;
  isActive: boolean;
  createdAt: string;
}

export interface Location {
  id: string;
  name: string;
  description?: string;
  city?: string;
  country?: string;
  postalCode?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  isActive: boolean;
  createdAt: string;
}

export interface Sensor {
  id: string;
  deviceId: string;
  name: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  isActive: boolean;
  isOnline: boolean;
  lastSeen?: string;
  createdAt: string;
  sensorType: {
    id: string;
    name: string;
    unit?: string;
  };
  location: {
    id: string;
    name: string;
    city?: string;
  };
}

export interface SensorReading {
  id: string;
  value: number;
  rawValue?: number;
  timestamp: string;
  receivedAt: string;
  sensor: {
    id: string;
    name: string;
    sensorType: {
      name: string;
      unit?: string;
    };
  };
}

export interface CreateSensorTypeInput {
  name: string;
  description?: string;
  unit?: string;
  dataType: string;
  minValue?: number;
  maxValue?: number;
}

export interface CreateLocationInput {
  name: string;
  description?: string;
  city?: string;
  country?: string;
  postalCode?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
}

export interface CreateSensorInput {
  deviceId: string;
  name: string;
  description?: string;
  sensorTypeId: string;
  locationId: string;
  manufacturer?: string;
  model?: string;
  firmwareVersion?: string;
  hardwareVersion?: string;
  samplingInterval?: number;
}

export interface CreateSensorReadingInput {
  sensorId: string;
  value: number;
  rawValue?: number;
  timestamp?: string;
}