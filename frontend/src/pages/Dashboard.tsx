import React, { useState, useEffect } from 'react';
import { useQuery } from '@apollo/client';
import { GET_SENSORS, GET_SENSOR_TYPES, GET_LOCATIONS, GET_LATEST_READINGS } from '../graphql/queries';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { Database, MapPin, Thermometer, Activity, Zap, TrendingUp, Wifi, Home, Battery, Lightbulb } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { data: sensorsData, loading: sensorsLoading, error: sensorsError } = useQuery(GET_SENSORS);
  const { data: sensorTypesData, loading: typesLoading } = useQuery(GET_SENSOR_TYPES);
  const { data: locationsData, loading: locationsLoading } = useQuery(GET_LOCATIONS);
  const { data: readingsData, loading: readingsLoading } = useQuery(GET_LATEST_READINGS);

  const [liveValue, setLiveValue] = useState(24.5);
  const [todayReadings, setTodayReadings] = useState(127);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveValue(prev => Math.max(15, prev + (Math.random() - 0.5) * 2));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  if (sensorsLoading || typesLoading || locationsLoading) return <LoadingSpinner />;
  if (sensorsError) return <ErrorMessage message={sensorsError.message} />;

  const totalSensors = sensorsData?.sensors?.length || 0;
  const onlineSensors = sensorsData?.sensors?.filter((s: any) => s.isOnline)?.length || 0;
  const totalSensorTypes = sensorTypesData?.sensorTypes?.length || 0;
  const totalLocations = locationsData?.locations?.length || 0;

  const getSensorIcon = (type: string) => {
    switch(type.toLowerCase()) {
      case 'temperature': return <Thermometer size={20} />;
      case 'humidity': return <Activity size={20} />;
      case 'pressure': return <Battery size={20} />;
      case 'light': return <Lightbulb size={20} />;
      case 'air quality': return <Zap size={20} />;
      default: return <Database size={20} />;
    }
  };

  const getStatusColor = (isOnline: boolean) => {
    return isOnline 
      ? 'bg-gradient-to-r from-cyan-500 to-blue-400' 
      : 'bg-gradient-to-r from-gray-500 to-gray-400';
  };

  const getLocationStats = () => {
    const locationMap = new Map();
    sensorsData?.sensors?.forEach((sensor: any) => {
      const locationName = sensor.location.name;
      if (!locationMap.has(locationName)) {
        locationMap.set(locationName, { online: 0, total: 0 });
      }
      locationMap.get(locationName).total++;
      if (sensor.isOnline) {
        locationMap.get(locationName).online++;
      }
    });
    return Array.from(locationMap.entries()).map(([name, stats]) => ({
      name,
      ...stats
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Header mit Live-Daten */}
      <div className="bg-gradient-to-r from-cyan-400 to-blue-500 p-6 rounded-b-3xl shadow-2xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
            <Database className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Sensor Hub</h1>
            <p className="text-white/80 text-sm">Smart Sensor Management</p>
          </div>
        </div>
        
        {/* Live Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/20">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp size={16} className="text-white/80" />
              <span className="text-white/80 text-sm">Live Reading</span>
            </div>
            <div className="text-white text-2xl font-bold">{liveValue.toFixed(1)}°C</div>
            <div className="text-white/70 text-xs">Average Temperature</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/20">
            <div className="flex items-center gap-2 mb-2">
              <Activity size={16} className="text-white/80" />
              <span className="text-white/80 text-sm">Active</span>
            </div>
            <div className="text-white text-2xl font-bold">{onlineSensors}/{totalSensors}</div>
            <div className="text-white/70 text-xs">Sensors Online</div>
          </div>
        </div>

        {/* Tagesübersicht */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/20">
          <div className="flex justify-between items-center mb-3">
            <span className="text-white font-medium">Today</span>
            <span className="text-white/80 text-sm">{todayReadings} readings</span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-white to-yellow-200 h-3 rounded-full transition-all duration-500 shadow-sm"
              style={{ width: `${Math.min((todayReadings / 200) * 100, 100)}%` }}
            ></div>
          </div>
          <div className="mt-2 text-white/70 text-xs flex justify-between">
            <span>Target: 200 readings</span>
            <span>Coverage: {Math.round((onlineSensors / totalSensors) * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 -mt-4">
        {/* Smart Sensoren */}
        <div className="mb-6">
          <h2 className="text-white text-xl font-bold mb-4 flex items-center gap-2">
            <Thermometer size={20} />
            Active Sensors
          </h2>
          
          <div className="space-y-3">
            {sensorsData?.sensors?.slice(0, 6).map((sensor: any) => (
              <div
                key={sensor.id}
                className="bg-gray-800/30 backdrop-blur-sm rounded-2xl p-4 border border-gray-700/50 hover:bg-gray-800/50 transition-all"
              >
                <div className="flex items-center gap-4">
                  {/* Sensor Icon & Status */}
                  <div className={`w-12 h-12 rounded-full ${getStatusColor(sensor.isOnline)} flex items-center justify-center text-white`}>
                    {getSensorIcon(sensor.sensorType.name)}
                  </div>
                  
                  {/* Sensor Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-white font-medium">{sensor.name}</span>
                      <span className="text-xs px-2 py-1 bg-gray-700/50 text-gray-300 rounded-full">
                        {sensor.location.name}
                      </span>
                      {sensor.isOnline && <Wifi size={12} className="text-cyan-400" />}
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className={`font-medium ${
                        sensor.isOnline ? 'text-cyan-400' : 'text-gray-400'
                      }`}>
                        {sensor.isOnline ? 'Online' : 'Offline'}
                      </span>
                      <span className="text-gray-400">
                        {sensor.sensorType.name}
                      </span>
                      <span className="text-gray-400">
                        {sensor.deviceId}
                      </span>
                    </div>
                  </div>
                  
                  {/* Status Indicator */}
                  <div className={`w-12 h-6 rounded-full transition-all ${
                    sensor.isOnline 
                      ? 'bg-cyan-500' 
                      : 'bg-gray-600'
                  }`}>
                    <div className={`w-5 h-5 bg-white rounded-full transition-all ${
                      sensor.isOnline ? 'translate-x-6' : 'translate-x-0.5'
                    }`}></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Location Overview */}
        <div>
          <h2 className="text-white text-xl font-bold mb-4 flex items-center gap-2">
            <MapPin size={20} />
            Location Status
          </h2>
          
          <div className="space-y-3">
            {getLocationStats().map((location, index) => (
              <div
                key={index}
                className="bg-gray-800/30 backdrop-blur-sm rounded-2xl p-4 border border-gray-700/50 hover:border-gray-600/50 transition-all"
              >
                <div className="flex items-center gap-4">
                  {/* Location Icon */}
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-indigo-400 flex items-center justify-center text-white">
                    <Home size={20} />
                  </div>
                  
                  {/* Location Info */}
                  <div className="flex-1">
                    <span className="block font-medium text-white">
                      {location.name}
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded-full">
                        {location.online}/{location.total} sensors
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round((location.online / location.total) * 100)}% online
                      </span>
                    </div>
                  </div>
                  
                  {/* Stats */}
                  <div className="text-right">
                    <div className="text-cyan-400 font-bold text-lg">
                      {location.online}
                    </div>
                    <div className="text-gray-400 text-xs">active</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="mt-8 bg-gradient-to-r from-cyan-600/20 to-blue-500/20 backdrop-blur-sm rounded-2xl p-6 border border-cyan-500/30">
          <div className="text-center">
            <div className="text-cyan-400 text-3xl font-bold mb-2">
              {Math.round((onlineSensors / totalSensors) * 100)}%
            </div>
            <div className="text-white/80 mb-4">System Health - All sensors monitored</div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-white font-medium">{totalSensors}</div>
                <div className="text-gray-400">Total Sensors</div>
              </div>
              <div>
                <div className="text-white font-medium">{totalLocations}</div>
                <div className="text-gray-400">Locations</div>
              </div>
              <div>
                <div className="text-white font-medium">{totalSensorTypes}</div>
                <div className="text-gray-400">Sensor Types</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;