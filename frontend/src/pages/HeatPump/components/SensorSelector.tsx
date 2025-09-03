import React from 'react';
import { ChevronDown } from 'lucide-react';
import type { HeatPumpSensor } from '../types/heatpump.types';

interface SensorSelectorProps {
  label: string;
  sensors: HeatPumpSensor[];
  selectedSensorId: string | null;
  onSelect: (sensorId: string) => void;
  loading?: boolean;
  error?: string | null;
  placeholder?: string;
}

const SensorSelector: React.FC<SensorSelectorProps> = ({
  label,
  sensors,
  selectedSensorId,
  onSelect,
  loading = false,
  error = null,
  placeholder = "Please select a sensor"
}) => {
  return (
    <div className="flex flex-col space-y-2">
      <label className="text-sm font-medium text-gray-700">
        {label}
      </label>
      
      <div className="relative">
        <select
          value={selectedSensorId || ''}
          onChange={(e) => onSelect(e.target.value)}
          disabled={loading || !!error}
          className={`
            appearance-none w-full px-3 py-2 border rounded-md shadow-sm text-sm
            ${error 
              ? 'border-red-300 bg-red-50 text-red-900' 
              : 'border-gray-300 bg-white text-gray-900'
            }
            ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          `}
        >
          <option value="" disabled>
            {loading ? 'Loading sensors...' : placeholder}
          </option>
          {sensors.map((sensor) => (
            <option key={sensor.id} value={sensor.id}>
              {sensor.name} ({sensor.sensorType.name})
              {sensor.description && ` - ${sensor.description}`}
            </option>
          ))}
        </select>
        
        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
      </div>
      
      {error && (
        <p className="text-sm text-red-600">
          Error loading sensors: {error}
        </p>
      )}
      
      {!loading && !error && sensors.length === 0 && (
        <p className="text-sm text-gray-500">
          No kWh sensors found. Please ensure you have sensors with kWh unit configured.
        </p>
      )}
    </div>
  );
};

export default SensorSelector;