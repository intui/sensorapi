import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@apollo/client';
import { GET_SENSORS, GET_SENSOR_READINGS } from '../../../graphql/queries';
import type { HeatPumpSensor, EnergyReading, TimeRange } from '../types/heatpump.types';

interface UseSensorDataProps {
  electricalSensorId: string | null;
  thermalSensorId: string | null;
  timeRange: TimeRange;
}

interface UseSensorDataReturn {
  electricalReadings: EnergyReading[];
  thermalReadings: EnergyReading[];
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export const useSensorData = ({
  electricalSensorId,
  thermalSensorId,
  timeRange
}: UseSensorDataProps): UseSensorDataReturn => {
  const [electricalReadings, setElectricalReadings] = useState<EnergyReading[]>([]);
  const [thermalReadings, setThermalReadings] = useState<EnergyReading[]>([]);

  // Fetch electrical sensor readings
  const {
    data: electricalData,
    loading: electricalLoading,
    error: electricalError,
    refetch: refetchElectrical
  } = useQuery(GET_SENSOR_READINGS, {
    variables: {
      sensorId: electricalSensorId,
      startTime: timeRange.startTime,
      endTime: timeRange.endTime,
      limit: 10000 // Generous limit for aggregated data
    },
    skip: !electricalSensorId,
    fetchPolicy: 'cache-and-network'
  });

  // Fetch thermal sensor readings
  const {
    data: thermalData,
    loading: thermalLoading,
    error: thermalError,
    refetch: refetchThermal
  } = useQuery(GET_SENSOR_READINGS, {
    variables: {
      sensorId: thermalSensorId,
      startTime: timeRange.startTime,
      endTime: timeRange.endTime,
      limit: 10000 // Generous limit for aggregated data
    },
    skip: !thermalSensorId,
    fetchPolicy: 'cache-and-network'
  });

  // Process electrical readings
  useEffect(() => {
    if (electricalData?.sensorReadings) {
      const readings: EnergyReading[] = electricalData.sensorReadings
        .map((reading: any) => ({
          timestamp: reading.timestamp,
          value: reading.value
        }))
        .sort((a: EnergyReading, b: EnergyReading) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
      setElectricalReadings(readings);
    }
  }, [electricalData]);

  // Process thermal readings
  useEffect(() => {
    if (thermalData?.sensorReadings) {
      const readings: EnergyReading[] = thermalData.sensorReadings
        .map((reading: any) => ({
          timestamp: reading.timestamp,
          value: reading.value
        }))
        .sort((a: EnergyReading, b: EnergyReading) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
      setThermalReadings(readings);
    }
  }, [thermalData]);

  const isLoading = electricalLoading || thermalLoading;
  const error = electricalError?.message || thermalError?.message || null;

  const refetch = () => {
    if (electricalSensorId) refetchElectrical();
    if (thermalSensorId) refetchThermal();
  };

  return {
    electricalReadings,
    thermalReadings,
    isLoading,
    error,
    refetch
  };
};

// Hook for fetching available sensors with kWh unit
export const useKwhSensors = () => {
  const { data, loading, error } = useQuery(GET_SENSORS, {
    variables: {
      activeOnly: true,
      onlineOnly: false
    },
    fetchPolicy: 'cache-and-network'
  });

  const kwhSensors = useMemo((): HeatPumpSensor[] => {
    if (!data?.sensors) return [];
    
    return data.sensors
      .filter((sensor: any) => sensor.sensorType?.unit === 'kWh')
      .map((sensor: any) => ({
        id: sensor.id,
        name: sensor.name,
        description: sensor.description,
        locationId: sensor.location?.id ?? null,
        sensorType: {
          id: sensor.sensorType.id,
          name: sensor.sensorType.name,
          unit: sensor.sensorType.unit
        }
      }));
  }, [data]);

  return {
    sensors: kwhSensors,
    loading,
    error: error?.message || null
  };
};