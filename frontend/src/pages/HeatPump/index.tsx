import React, { useState, useMemo, useEffect } from 'react';
import { Activity } from 'lucide-react';
import SensorSelector from './components/SensorSelector';
import TimeControls from './components/TimeControls';
import EnergyChart from './components/EnergyChart';
import COPChart from './components/COPChart';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useKwhSensors } from './hooks/useSensorData';
import { useOptimizedCOPData } from './hooks/useOptimizedCOPData';
import type {
  TimeRangeType,
  AggregationType,
  TimeRange,
  SensorSelection
} from './types/heatpump.types';

const HeatPumpPage: React.FC = () => {
  const [sensorSelection, setSensorSelection] = useState<SensorSelection>({
    electricalSensorId: null,
    thermalSensorId: null
  });

  const [timeRange, setTimeRange] = useState<TimeRangeType>('7d');
  const [aggregation, setAggregation] = useState<AggregationType>('day');
  const [customStartDate, setCustomStartDate] = useState<string>('');
  const [customEndDate, setCustomEndDate] = useState<string>('');

  // Calculate actual time range based on selection
  const actualTimeRange: TimeRange = useMemo(() => {
    const now = new Date();
    let startTime = new Date();

    if (timeRange === 'custom') {
      if (customStartDate && customEndDate) {
        return {
          startTime: customStartDate,
          endTime: customEndDate
        };
      }
      // Fallback to 24h if custom dates not set
      startTime.setDate(now.getDate() - 1);
    } else {
      switch (timeRange) {
        case '24h':
          startTime.setDate(now.getDate() - 1);
          break;
        case '7d':
          startTime.setDate(now.getDate() - 7);
          break;
        case '30d':
          startTime.setDate(now.getDate() - 30);
          break;
      }
    }

    return {
      startTime: startTime.toISOString(),
      endTime: now.toISOString()
    };
  }, [timeRange, customStartDate, customEndDate]);

  // Fetch available sensors
  const {
    sensors: kwhSensors,
    loading: sensorsLoading,
    error: sensorsError
  } = useKwhSensors();

  // Auto-select default sensors when available
  useEffect(() => {
    if (kwhSensors.length > 0 && !sensorSelection.electricalSensorId && !sensorSelection.thermalSensorId) {
      // Default sensor names from the screenshot
      const defaultElectricalSensorName = 'wärmepumpe_Energie_sum';
      const defaultThermalSensorName = 'idm_aero_hp_wärmemenge_warmwasser';

      // Find sensors by name (partial match to handle description text)
      const electricalSensor = kwhSensors.find(sensor =>
        sensor.name.includes(defaultElectricalSensorName)
      );
      const thermalSensor = kwhSensors.find(sensor =>
        sensor.name.includes(defaultThermalSensorName)
      );

      if (electricalSensor || thermalSensor) {
        setSensorSelection({
          electricalSensorId: electricalSensor?.id || null,
          thermalSensorId: thermalSensor?.id || null
        });
      }
    }
  }, [kwhSensors, sensorSelection.electricalSensorId, sensorSelection.thermalSensorId]);

  // Use optimized COP data fetching (replaces both useSensorData + useCOPCalculation)
  const {
    copData,
    isLoading: dataLoading,
    error: dataError
  } = useOptimizedCOPData({
    electricalSensorId: sensorSelection.electricalSensorId,
    thermalSensorId: sensorSelection.thermalSensorId,
    timeRange: actualTimeRange,
    aggregation
  });

  const handleElectricalSensorChange = (sensorId: string) => {
    setSensorSelection(prev => ({
      ...prev,
      electricalSensorId: sensorId
    }));
  };

  const handleThermalSensorChange = (sensorId: string) => {
    setSensorSelection(prev => ({
      ...prev,
      thermalSensorId: sensorId
    }));
  };

  const isDataAvailable = sensorSelection.electricalSensorId && sensorSelection.thermalSensorId;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Heat Pump Performance</h1>
            <p className="text-sm text-gray-600">
              Monitor energy consumption, production, and efficiency
            </p>
          </div>
        </div>
      </div>

      {/* Sensor Selection */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Sensor Selection</h2>

        {sensorsLoading ? (
          <div className="py-8">
            <LoadingSpinner />
            <p className="text-center text-gray-500 mt-4">Loading available sensors...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SensorSelector
                label="Electrical Energy Sensor"
                sensors={kwhSensors}
                selectedSensorId={sensorSelection.electricalSensorId}
                onSelect={handleElectricalSensorChange}
                loading={sensorsLoading}
                error={sensorsError}
                placeholder="Select electrical energy sensor"
              />
              <SensorSelector
                label="Thermal Energy Sensor"
                sensors={kwhSensors}
                selectedSensorId={sensorSelection.thermalSensorId}
                onSelect={handleThermalSensorChange}
                loading={sensorsLoading}
                error={sensorsError}
                placeholder="Select thermal energy sensor"
              />
            </div>

            {/* Sensor Selection Status */}
            {!sensorsLoading && kwhSensors.length === 0 && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-sm text-yellow-800">
                  <strong>No kWh sensors found.</strong> Please ensure you have configured sensors with kWh unit type
                  in your sensor management system.
                </p>
              </div>
            )}

            {sensorSelection.electricalSensorId && sensorSelection.thermalSensorId && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-green-800">
                  <strong>Ready!</strong> Both sensors selected. Configure time range and view your heat pump performance below.
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Time Controls */}
      <TimeControls
        timeRange={timeRange}
        aggregation={aggregation}
        onTimeRangeChange={setTimeRange}
        onAggregationChange={setAggregation}
        customStartDate={customStartDate}
        customEndDate={customEndDate}
        onCustomStartDateChange={setCustomStartDate}
        onCustomEndDateChange={setCustomEndDate}
      />

      {/* Charts */}
      <div className="space-y-6">
        <EnergyChart
          copData={copData}
          isLoading={dataLoading}
          error={dataError}
        />

        <COPChart
          copData={copData}
          isLoading={dataLoading}
          error={dataError}
        />
      </div>

      {/* Data Summary */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Summary</h3>
        {dataLoading ? (
          <div className="py-8">
            <LoadingSpinner />
            <p className="text-center text-gray-500 mt-4">Loading performance data...</p>
          </div>
        ) : isDataAvailable && copData.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm font-medium text-blue-600">Total Electrical Energy</div>
              <div className="text-2xl font-bold text-blue-900">
                {copData.reduce((sum: number, item) => sum + item.electricalEnergy, 0).toFixed(2)} kWh
              </div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-sm font-medium text-orange-600">Total Thermal Energy</div>
              <div className="text-2xl font-bold text-orange-900">
                {copData.reduce((sum: number, item) => sum + item.thermalEnergy, 0).toFixed(2)} kWh
              </div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm font-medium text-green-600">Average COP</div>
              <div className="text-2xl font-bold text-green-900">
                {(() => {
                  const validCops = copData.filter(item => item.cop !== null).map(item => item.cop!);
                  if (validCops.length === 0) return 'N/A';
                  const avgCop = validCops.reduce((sum: number, cop: number) => sum + cop, 0) / validCops.length;
                  return avgCop.toFixed(2);
                })()}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            {sensorSelection.electricalSensorId && sensorSelection.thermalSensorId
              ? "No data available for selected time range"
              : "Select sensors and configure settings to view performance summary"
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default HeatPumpPage;