export interface HeatPumpSensor {
  id: string;
  name: string;
  description?: string;
  sensorType: {
    id: string;
    name: string;
    unit: string;
  };
}

export interface EnergyReading {
  timestamp: string;
  value: number;
}

export interface EnergyData {
  electricalReadings: EnergyReading[];
  thermalReadings: EnergyReading[];
}

export interface COPCalculation {
  timestamp: string;
  electricalEnergy: number;
  thermalEnergy: number;
  cop: number | null;
  _sortDate?: string; // Internal field for proper chronological sorting
}

export interface TimeRange {
  startTime: string;
  endTime: string;
}

export type AggregationType = 'hour' | 'day' | 'month';
export type TimeRangeType = '24h' | '7d' | '30d' | 'custom';

export interface ChartDataPoint {
  x: string;
  y: number;
}

export interface EnergyChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
  }[];
}

export interface COPChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
  }[];
}

export interface SensorSelection {
  electricalSensorId: string | null;
  thermalSensorId: string | null;
}

export interface HeatPumpState {
  sensorSelection: SensorSelection;
  timeRange: TimeRangeType;
  aggregation: AggregationType;
  customTimeRange: TimeRange | null;
  isLoading: boolean;
  error: string | null;
}