import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@apollo/client';
import { GET_SENSOR_READINGS, GET_SENSORS, GET_LOCATIONS, GET_SENSOR_TYPES } from '../graphql/queries';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { Line, Bar, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { 
  Calendar, 
  TrendingUp, 
  Download, 
  RefreshCw, 
  Settings, 
  BarChart3, 
  LineChart, 
  Scatter3D,
  Filter,
  Search,
  MapPin,
  Activity,
  Clock,
  Eye,
  EyeOff,
  Plus,
  X
} from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

interface SelectedSensor {
  id: string;
  color: string;
  visible: boolean;
}

type ChartType = 'line' | 'bar' | 'scatter';
type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d' | 'custom';

const CHART_COLORS = [
  'rgb(59, 130, 246)',   // blue
  'rgb(239, 68, 68)',    // red
  'rgb(34, 197, 94)',    // green
  'rgb(168, 85, 247)',   // purple
  'rgb(245, 158, 11)',   // orange
  'rgb(236, 72, 153)',   // pink
  'rgb(20, 184, 166)',   // teal
  'rgb(99, 102, 241)',   // indigo
];

const SensorReadings: React.FC = () => {
  const [selectedSensors, setSelectedSensors] = useState<SelectedSensor[]>([]);
  const [timeRange, setTimeRange] = useState<TimeRange>('24h');
  const [customStartDate, setCustomStartDate] = useState<string>('');
  const [customEndDate, setCustomEndDate] = useState<string>('');
  const [chartType, setChartType] = useState<ChartType>('line');
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [refreshInterval, setRefreshInterval] = useState<number>(30);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [selectedSensorType, setSelectedSensorType] = useState<string>('');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState<boolean>(false);
  const [dataLimit, setDataLimit] = useState<number>(1000);

  const timeRangeFilters = useMemo(() => {
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
        case '1h':
          startTime.setHours(now.getHours() - 1);
          break;
        case '6h':
          startTime.setHours(now.getHours() - 6);
          break;
        case '24h':
          startTime.setDate(now.getDate() - 1);
          break;
        case '7d':
          startTime.setDate(now.getDate() - 7);
          break;
        case '30d':
          startTime.setDate(now.getDate() - 30);
          break;
        default:
          startTime.setDate(now.getDate() - 1);
      }
    }
    
    return {
      startTime: startTime.toISOString(),
      endTime: now.toISOString()
    };
  }, [timeRange, customStartDate, customEndDate]);

  // Fetch all data needed
  const { data: sensorsData } = useQuery(GET_SENSORS, {
    variables: {
      locationId: selectedLocation || undefined,
      sensorTypeId: selectedSensorType || undefined,
      activeOnly: true,
      onlineOnly: false
    }
  });
  
  const { data: locationsData } = useQuery(GET_LOCATIONS);
  const { data: sensorTypesData } = useQuery(GET_SENSOR_TYPES);

  const sensors = sensorsData?.sensors || [];
  const locations = locationsData?.locations || [];
  const sensorTypes = sensorTypesData?.sensorTypes || [];

  // Filter sensors based on search
  const filteredSensors = sensors.filter((sensor: any) => 
    sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sensor.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sensor.location.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sensor.sensorType.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      // Trigger refetch for all selected sensors
      selectedSensors.forEach(sensor => {
        if (sensor.visible) {
          // This will be handled by the individual sensor reading queries
        }
      });
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, selectedSensors]);

  const addSensor = (sensorId: string) => {
    if (!selectedSensors.find(s => s.id === sensorId)) {
      const colorIndex = selectedSensors.length % CHART_COLORS.length;
      setSelectedSensors(prev => [...prev, {
        id: sensorId,
        color: CHART_COLORS[colorIndex],
        visible: true
      }]);
    }
  };

  const removeSensor = (sensorId: string) => {
    setSelectedSensors(prev => prev.filter(s => s.id !== sensorId));
  };

  const toggleSensorVisibility = (sensorId: string) => {
    setSelectedSensors(prev => prev.map(s => 
      s.id === sensorId ? { ...s, visible: !s.visible } : s
    ));
  };

  const getTimeRangeLabel = (range: TimeRange) => {
    switch (range) {
      case '1h': return 'Last Hour';
      case '6h': return 'Last 6 Hours';
      case '24h': return 'Last 24 Hours';
      case '7d': return 'Last 7 Days';
      case '30d': return 'Last 30 Days';
      case 'custom': return 'Custom Range';
      default: return 'Select Range';
    }
  };

  const exportData = () => {
    // TODO: Implement data export functionality
    alert('Export functionality will be implemented soon!');
  };

  const SensorReadingChart = ({ sensorId, color, visible }: { sensorId: string, color: string, visible: boolean }) => {
    const { data: readingsData, loading, error, refetch } = useQuery(GET_SENSOR_READINGS, {
      variables: {
        sensorId,
        limit: dataLimit,
        ...timeRangeFilters,
      },
      skip: !visible,
      pollInterval: autoRefresh ? refreshInterval * 1000 : 0,
    });

    const readings = readingsData?.sensorReadings || [];
    const sensor = sensors.find((s: any) => s.id === sensorId);

    if (!visible || !sensor) return null;

    return {
      readings,
      sensor,
      loading,
      error,
      color
    };
  };

  // Collect all sensor data for the chart
  const allSensorData = selectedSensors.map(({ id, color, visible }) => {
    const { data: readingsData, loading, error } = useQuery(GET_SENSOR_READINGS, {
      variables: {
        sensorId: id,
        limit: dataLimit,
        ...timeRangeFilters,
      },
      skip: !visible,
      pollInterval: autoRefresh ? refreshInterval * 1000 : 0,
    });

    const readings = readingsData?.sensorReadings || [];
    const sensor = sensors.find((s: any) => s.id === id);

    return {
      sensorId: id,
      sensor,
      readings,
      color,
      visible,
      loading,
      error
    };
  }).filter(data => data.visible && data.sensor);

  const isLoading = allSensorData.some(data => data.loading);
  const hasError = allSensorData.some(data => data.error);
  const errors = allSensorData.filter(data => data.error).map(data => data.error);

  // Prepare chart data
  const chartData = useMemo(() => {
    if (allSensorData.length === 0) return { labels: [], datasets: [] };

    // Collect all unique timestamps
    const allTimestamps = new Set<string>();
    allSensorData.forEach(data => {
      data.readings.forEach((reading: any) => {
        allTimestamps.add(reading.timestamp);
      });
    });

    const sortedTimestamps = Array.from(allTimestamps).sort();
    
    const datasets = allSensorData.map(data => {
      const { sensor, readings, color } = data;
      
      // Create data points aligned with timestamps
      const dataPoints = sortedTimestamps.map(timestamp => {
        const reading = readings.find((r: any) => r.timestamp === timestamp);
        return reading ? reading.value : null;
      });

      const baseConfig = {
        label: `${sensor.name} (${sensor.sensorType.unit || 'value'})`,
        data: chartType === 'scatter' 
          ? readings.map((r: any) => ({ x: new Date(r.timestamp), y: r.value }))
          : dataPoints,
        borderColor: color,
        backgroundColor: chartType === 'bar' ? color + '80' : color + '20',
        borderWidth: 2,
        tension: chartType === 'line' ? 0.1 : 0,
      };

      if (chartType === 'line') {
        return {
          ...baseConfig,
          fill: false,
          pointRadius: 1,
          pointHoverRadius: 4,
        };
      } else if (chartType === 'bar') {
        return {
          ...baseConfig,
          type: 'bar' as const,
        };
      } else {
        return {
          ...baseConfig,
          showLine: false,
          pointRadius: 2,
        };
      }
    });

    return {
      labels: chartType === 'scatter' ? [] : sortedTimestamps.map(ts => new Date(ts)),
      datasets
    };
  }, [allSensorData, chartType]);

  const chartOptions = useMemo(() => {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: `Sensor Readings - ${getTimeRangeLabel(timeRange)}`,
        },
        tooltip: {
          mode: 'index' as const,
          intersect: false,
          callbacks: {
            label: (context: any) => {
              const sensor = allSensorData[context.datasetIndex]?.sensor;
              const unit = sensor?.sensorType?.unit || '';
              return `${context.dataset.label}: ${context.parsed.y}${unit ? ' ' + unit : ''}`;
            }
          }
        },
      },
      scales: {
        x: {
          type: chartType === 'scatter' ? 'time' : 'time',
          time: {
            displayFormats: {
              hour: 'HH:mm',
              day: 'MMM dd',
              week: 'MMM dd',
              month: 'MMM yyyy'
            },
          },
          title: {
            display: true,
            text: 'Time'
          }
        },
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: allSensorData.length === 1 
              ? allSensorData[0].sensor?.sensorType?.unit || 'Value'
              : 'Value'
          }
        },
      },
      interaction: {
        intersect: false,
        mode: 'index' as const,
      },
    };

    return baseOptions;
  }, [allSensorData, chartType, timeRange]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Sensor Readings Dashboard</h1>
        <div className="flex items-center space-x-3">
          <button
            onClick={exportData}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`inline-flex items-center px-3 py-2 border rounded-md shadow-sm text-sm font-medium ${
              autoRefresh 
                ? 'border-green-300 text-green-700 bg-green-50 hover:bg-green-100' 
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
            }`}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </button>
        </div>
      </div>

      {/* Controls Panel */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          {/* Main Controls Row */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-4">
            {/* Time Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="h-4 w-4 inline mr-1" />
                Time Range
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value as TimeRange)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="1h">Last Hour</option>
                <option value="6h">Last 6 Hours</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>

            {/* Chart Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <BarChart3 className="h-4 w-4 inline mr-1" />
                Chart Type
              </label>
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value as ChartType)}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="scatter">Scatter Plot</option>
              </select>
            </div>

            {/* Data Limit */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Activity className="h-4 w-4 inline mr-1" />
                Data Points
              </label>
              <select
                value={dataLimit}
                onChange={(e) => setDataLimit(parseInt(e.target.value))}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value={500}>500 points</option>
                <option value={1000}>1,000 points</option>
                <option value={2000}>2,000 points</option>
                <option value={5000}>5,000 points</option>
                <option value={10000}>10,000 points</option>
              </select>
            </div>

            {/* Advanced Filters Toggle */}
            <div className="flex items-end">
              <button
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Filter className="h-4 w-4 mr-2" />
                {showAdvancedFilters ? 'Hide' : 'Show'} Filters
              </button>
            </div>
          </div>

          {/* Custom Date Range */}
          {timeRange === 'custom' && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          )}

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="border-t pt-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 mb-4">
                {/* Search */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Search className="h-4 w-4 inline mr-1" />
                    Search Sensors
                  </label>
                  <input
                    type="text"
                    placeholder="Search by name, type, or location..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Location Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MapPin className="h-4 w-4 inline mr-1" />
                    Location
                  </label>
                  <select
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">All Locations</option>
                    {locations.map((location: any) => (
                      <option key={location.id} value={location.id}>
                        {location.name} ({location.city})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sensor Type Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Settings className="h-4 w-4 inline mr-1" />
                    Sensor Type
                  </label>
                  <select
                    value={selectedSensorType}
                    onChange={(e) => setSelectedSensorType(e.target.value)}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">All Types</option>
                    {sensorTypes.map((type: any) => (
                      <option key={type.id} value={type.id}>
                        {type.name} ({type.unit})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Auto Refresh Settings */}
              {autoRefresh && (
                <div className="flex items-center space-x-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Refresh Interval (seconds):
                  </label>
                  <select
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                    className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={10}>10s</option>
                    <option value={30}>30s</option>
                    <option value={60}>1m</option>
                    <option value={300}>5m</option>
                  </select>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Sensor Selection */}
      <div className="bg-white shadow rounded-lg">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Available Sensors</h3>
            <div className="text-sm text-gray-500">
              {filteredSensors.length} of {sensors.length} sensors
            </div>
          </div>

          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filteredSensors.map((sensor: any) => {
              const isSelected = selectedSensors.find(s => s.id === sensor.id);
              return (
                <div
                  key={sensor.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                  onClick={() => isSelected ? removeSensor(sensor.id) : addSensor(sensor.id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {sensor.name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {sensor.sensorType.name} • {sensor.location.name}
                      </p>
                      <p className="text-xs text-gray-400">
                        {sensor.isOnline ? '🟢 Online' : '🔴 Offline'}
                      </p>
                    </div>
                    <div className="ml-2">
                      {isSelected ? (
                        <X className="h-4 w-4 text-red-500" />
                      ) : (
                        <Plus className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Selected Sensors Overview */}
      {selectedSensors.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Selected Sensors</h3>
              <div className="text-sm text-gray-500">
                {selectedSensors.filter(s => s.visible).length} visible of {selectedSensors.length} selected
              </div>
            </div>
            
            <div className="space-y-2">
              {selectedSensors.map((selectedSensor) => {
                const sensor = sensors.find((s: any) => s.id === selectedSensor.id);
                if (!sensor) return null;
                
                return (
                  <div key={selectedSensor.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full border-2"
                        style={{ backgroundColor: selectedSensor.color, borderColor: selectedSensor.color }}
                      />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{sensor.name}</p>
                        <p className="text-xs text-gray-500">
                          {sensor.sensorType.name} • {sensor.location.name}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleSensorVisibility(selectedSensor.id)}
                        className={`p-1 rounded ${
                          selectedSensor.visible 
                            ? 'text-gray-600 hover:text-gray-800' 
                            : 'text-gray-400 hover:text-gray-600'
                        }`}
                      >
                        {selectedSensor.visible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                      </button>
                      <button
                        onClick={() => removeSensor(selectedSensor.id)}
                        className="p-1 text-red-500 hover:text-red-700"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Chart Display */}
      {selectedSensors.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">
                  {getTimeRangeLabel(timeRange)} - Multiple Sensors
                </h3>
              </div>
              <div className="flex items-center space-x-2">
                {chartType === 'line' && <LineChart className="h-5 w-5 text-gray-400" />}
                {chartType === 'bar' && <BarChart3 className="h-5 w-5 text-gray-400" />}
                {chartType === 'scatter' && <Scatter3D className="h-5 w-5 text-gray-400" />}
                <span className="text-sm text-gray-500">
                  {allSensorData.reduce((total, data) => total + data.readings.length, 0)} total readings
                </span>
              </div>
            </div>
            
            {isLoading && <LoadingSpinner />}
            {hasError && (
              <div className="space-y-2">
                {errors.map((error, index) => (
                  <ErrorMessage key={index} message={error?.message || 'Unknown error'} />
                ))}
              </div>
            )}
            
            {!isLoading && !hasError && allSensorData.some(data => data.readings.length > 0) && (
              <div className="h-96">
                {chartType === 'line' && <Line data={chartData} options={chartOptions} />}
                {chartType === 'bar' && <Bar data={chartData} options={chartOptions} />}
                {chartType === 'scatter' && <Scatter data={chartData} options={chartOptions} />}
              </div>
            )}
            
            {!isLoading && !hasError && allSensorData.every(data => data.readings.length === 0) && (
              <div className="text-center py-12">
                <div className="text-gray-500">
                  No readings found for the selected sensors and time range.
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Statistics Panel */}
      {selectedSensors.length > 0 && allSensorData.some(data => data.readings.length > 0) && (
        <div className="bg-white shadow rounded-lg">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Statistics Overview
            </h3>
            
            <div className="space-y-6">
              {allSensorData.filter(data => data.readings.length > 0).map((data) => {
                const { sensor, readings, color } = data;
                const values = readings.map((r: any) => r.value);
                const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
                const min = Math.min(...values);
                const max = Math.max(...values);
                const latest = readings[0]?.value;
                
                return (
                  <div key={sensor.id} className="border rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <div 
                        className="w-3 h-3 rounded-full mr-3"
                        style={{ backgroundColor: color }}
                      />
                      <h4 className="font-medium text-gray-900">
                        {sensor.name} ({sensor.sensorType.name})
                      </h4>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="text-xs font-medium text-gray-500 mb-1">Latest</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {latest?.toFixed(2)}
                          {sensor.sensorType.unit && (
                            <span className="text-xs text-gray-500 ml-1">
                              {sensor.sensorType.unit}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="text-xs font-medium text-gray-500 mb-1">Average</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {avg.toFixed(2)}
                          {sensor.sensorType.unit && (
                            <span className="text-xs text-gray-500 ml-1">
                              {sensor.sensorType.unit}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="text-xs font-medium text-gray-500 mb-1">Minimum</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {min.toFixed(2)}
                          {sensor.sensorType.unit && (
                            <span className="text-xs text-gray-500 ml-1">
                              {sensor.sensorType.unit}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="text-xs font-medium text-gray-500 mb-1">Maximum</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {max.toFixed(2)}
                          {sensor.sensorType.unit && (
                            <span className="text-xs text-gray-500 ml-1">
                              {sensor.sensorType.unit}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 text-xs text-gray-500">
                      {readings.length} readings • {sensor.location.name}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Welcome Message */}
      {selectedSensors.length === 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="p-12 text-center">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Sensor Readings Dashboard
            </h3>
            <p className="text-gray-500 mb-4">
              Select one or more sensors from the "Available Sensors" section above to start viewing real-time data.
            </p>
            <div className="text-sm text-gray-400">
              💡 You can compare multiple sensors, switch between chart types, and set up auto-refresh for live monitoring.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
  );
};

export default SensorReadings;