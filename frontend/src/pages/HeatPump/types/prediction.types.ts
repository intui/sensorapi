export interface WeatherForecastPoint {
  timestamp: string;
  temperature: number;
  humidity: number | null;
  windSpeed: number | null;
  precipitation: number | null;
  cloudCover: number | null;
}

export interface EnergyPredictionPoint {
  timestamp: string;
  temperature: number;
  predictedElectricalKwh: number;
  predictedThermalKwh: number;
  predictedCop: number | null;
  confidenceLowElectrical: number;
  confidenceHighElectrical: number;
  confidenceLowThermal: number;
  confidenceHighThermal: number;
}

export interface ModelInfo {
  r2Electrical: number;
  r2Thermal: number;
  trainingSamples: number;
  trainedAt: string;
  featureNames: string[];
}

export interface PredictionResult {
  predictions: EnergyPredictionPoint[];
  totalElectricalKwh: number;
  totalThermalKwh: number;
  averageCop: number | null;
  modelInfo: ModelInfo;
}

export type PredictionHorizon = '24h' | '96h';
