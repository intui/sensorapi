import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@apollo/client';
import { GET_SENSOR_READINGS, GET_SENSORS } from '../graphql/queries';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Calendar, TrendingUp } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const SensorReadings: React.FC = () => {
  const [selectedSensorId, setSelectedSensorId] = useState<string>('');
  const [timeRange, setTimeRange] = useState<string>('24h');

  const timeRangeFilters = useMemo(() => {
    const now = new Date();
    const startTime = new Date();
    
    switch (timeRange) {
      case '1h':
        startTime.setHours(now.getHours() - 1);
        break;
      case '24h':
        startTime.setDate(now.getDate() - 1);
        break;
      case '7d':
        startTime.setDate(now.getDate() - 7);
        break;
      default:
        startTime.setDate(now.getDate() - 1);
    }
    
    return {
      startTime: startTime.toISOString(),
      endTime: now.toISOString()
    };
  }, [timeRange]);

  const { data: sensorsData } = useQuery(GET_SENSORS);
  const { data: readingsData, loading, error, refetch } = useQuery(GET_SENSOR_READINGS, {
    variables: {
      sensorId: selectedSensorId,
      limit: 3000, // Optimales Limit für gute Performance und Details
      ...timeRangeFilters,
    },
    skip: !selectedSensorId,
  });

  // Refetch data when time range changes
  useEffect(() => {
    if (selectedSensorId) {
      refetch({
        sensorId: selectedSensorId,
        limit: 3000,
        ...timeRangeFilters,
      });
    }
  }, [timeRange, selectedSensorId]); // Removed refetch and timeRangeFilters from dependencies

  const sensors = sensorsData?.sensors || [];
  const readings = readingsData?.sensorReadings || [];

  // Debug logging
  console.log('SensorReadings Debug:', {
    selectedSensorId,
    timeRange,
    timeRangeFilters,
    sensorsCount: sensors.length,
    readingsCount: readings.length,
    loading,
    error: error?.message,
    readingsData
  });

  const selectedSensor = sensors.find((s: any) => s.id === selectedSensorId);

  const chartData = {
    labels: readings.map((reading: any) => new Date(reading.timestamp)),
    datasets: [
      {
        label: selectedSensor 
          ? `${selectedSensor.name} (${selectedSensor.sensorType.unit || 'value'})`
          : 'Sensor Reading',
        data: readings.map((reading: any) => reading.value),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0, // Changed from 0.4 to 0 for straight lines
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: selectedSensor ? `${selectedSensor.name} - Readings Over Time` : 'Sensor Readings',
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          displayFormats: {
            hour: 'HH:mm',
            day: 'MMM dd',
          },
        },
      },
      y: {
        beginAtZero: false,
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  const getTimeRangeLabel = (range: string) => {
    switch (range) {
      case '1h': return 'Last Hour';
      case '24h': return 'Last 24 Hours';
      case '7d': return 'Last 7 Days';
      default: return 'Select Range';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Sensor Readings</h1>
      </div>

      <div className="bg-white shadow rounded-lg mb-6">
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Sensor
              </label>
              <select
                value={selectedSensorId}
                onChange={(e) => setSelectedSensorId(e.target.value)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Choose a sensor...</option>
                {sensors.map((sensor: any) => (
                  <option key={sensor.id} value={sensor.id}>
                    {sensor.name} - {sensor.sensorType.name} ({sensor.location.name})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Range
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                disabled={!selectedSensorId}
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => refetch({
                  sensorId: selectedSensorId,
                  limit: 3000,
                  ...timeRangeFilters,
                })}
                disabled={!selectedSensorId || loading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {selectedSensorId && (
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">
                  {getTimeRangeLabel(timeRange)} - {readings.length} readings
                </h3>
              </div>
              {selectedSensor && (
                <div className="text-sm text-gray-500">
                  {selectedSensor.sensorType.name} sensor at {selectedSensor.location.name}
                </div>
              )}
            </div>
            
            {loading && <LoadingSpinner />}
            {error && <ErrorMessage message={error.message} />}
            
            {!loading && !error && readings.length > 0 && (
              <div className="h-96">
                <Line data={chartData} options={chartOptions} />
              </div>
            )}
            
            {!loading && !error && readings.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-500">
                  No readings found for the selected sensor and time range.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {selectedSensorId && readings.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Reading Statistics
            </h3>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Latest Value</div>
                <div className="text-2xl font-semibold text-gray-900">
                  {readings[0]?.value?.toFixed(2)}
                  {selectedSensor?.sensorType.unit && (
                    <span className="text-sm text-gray-500 ml-1">
                      {selectedSensor.sensorType.unit}
                    </span>
                  )}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Average</div>
                <div className="text-2xl font-semibold text-gray-900">
                  {readings.length > 0 && (
                    readings.reduce((sum: number, r: any) => sum + r.value, 0) / readings.length
                  ).toFixed(2)}
                  {selectedSensor?.sensorType.unit && (
                    <span className="text-sm text-gray-500 ml-1">
                      {selectedSensor.sensorType.unit}
                    </span>
                  )}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Minimum</div>
                <div className="text-2xl font-semibold text-gray-900">
                  {Math.min(...readings.map((r: any) => r.value)).toFixed(2)}
                  {selectedSensor?.sensorType.unit && (
                    <span className="text-sm text-gray-500 ml-1">
                      {selectedSensor.sensorType.unit}
                    </span>
                  )}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Maximum</div>
                <div className="text-2xl font-semibold text-gray-900">
                  {Math.max(...readings.map((r: any) => r.value)).toFixed(2)}
                  {selectedSensor?.sensorType.unit && (
                    <span className="text-sm text-gray-500 ml-1">
                      {selectedSensor.sensorType.unit}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SensorReadings;