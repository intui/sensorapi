import React from 'react';
import { Calendar, Clock } from 'lucide-react';
import type { TimeRangeType, AggregationType } from '../types/heatpump.types';

interface TimeControlsProps {
  timeRange: TimeRangeType;
  aggregation: AggregationType;
  onTimeRangeChange: (timeRange: TimeRangeType) => void;
  onAggregationChange: (aggregation: AggregationType) => void;
  customStartDate?: string;
  customEndDate?: string;
  onCustomStartDateChange?: (date: string) => void;
  onCustomEndDateChange?: (date: string) => void;
}

const TimeControls: React.FC<TimeControlsProps> = ({
  timeRange,
  aggregation,
  onTimeRangeChange,
  onAggregationChange,
  customStartDate,
  customEndDate,
  onCustomStartDateChange,
  onCustomEndDateChange
}) => {
  const timeRangeOptions = [
    { value: '24h' as const, label: 'Last 24 Hours' },
    { value: '7d' as const, label: 'Last 7 Days' },
    { value: '30d' as const, label: 'Last 30 Days' },
    { value: 'custom' as const, label: 'Custom Range' }
  ];

  const aggregationOptions = [
    { value: 'hour' as const, label: 'Hourly' },
    { value: 'day' as const, label: 'Daily' },
    { value: 'month' as const, label: 'Monthly' }
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <div className="flex flex-wrap gap-4 items-end">
        {/* Time Range Selector */}
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-700 flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            Time Range
          </label>
          <select
            value={timeRange}
            onChange={(e) => onTimeRangeChange(e.target.value as TimeRangeType)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm bg-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {timeRangeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Custom Date Range */}
        {timeRange === 'custom' && (
          <>
            <div className="flex flex-col space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Start Date
              </label>
              <input
                type="datetime-local"
                value={customStartDate || ''}
                onChange={(e) => onCustomStartDateChange?.(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="flex flex-col space-y-2">
              <label className="text-sm font-medium text-gray-700">
                End Date
              </label>
              <input
                type="datetime-local"
                value={customEndDate || ''}
                onChange={(e) => onCustomEndDateChange?.(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </>
        )}

        {/* Aggregation Selector */}
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-700 flex items-center">
            <Clock className="h-4 w-4 mr-1" />
            Aggregation
          </label>
          <select
            value={aggregation}
            onChange={(e) => onAggregationChange(e.target.value as AggregationType)}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm bg-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {aggregationOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Refresh Button */}
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium text-gray-700 opacity-0">
            Actions
          </label>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default TimeControls;