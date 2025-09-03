import React, { useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from 'chart.js';
import type { COPCalculation } from '../types/heatpump.types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface COPChartProps {
  copData: COPCalculation[];
  isLoading?: boolean;
  error?: string | null;
}

const COPChart: React.FC<COPChartProps> = ({
  copData,
  isLoading = false,
  error = null
}) => {
  const chartData = useMemo(() => {
    if (!copData || copData.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }

    // Filter out null COP values for chart display
    const validData = copData.filter(item => item.cop !== null);

    // Function to interpolate between red and green based on COP value
    const getCOPColor = (copValue: number) => {
      // Clamp COP value between 3 and 5
      const clampedCop = Math.max(3, Math.min(5, copValue));
      
      // Calculate the ratio from 0 (COP=3) to 1 (COP=5)
      const ratio = (clampedCop - 3) / (5 - 3);
      
      // Interpolate between red (255,0,0) and green (0,255,0)
      const red = Math.round(255 * (1 - ratio));
      const green = Math.round(255 * ratio);
      const blue = 0;
      
      return {
        background: `rgba(${red}, ${green}, ${blue}, 0.8)`,
        border: `rgb(${red}, ${green}, ${blue})`
      };
    };

    return {
      labels: validData.map(item => item.timestamp),
      datasets: [
        {
          label: 'Coefficient of Performance (COP)',
          data: validData.map(item => item.cop || 0),
          backgroundColor: (context: any) => {
            const value = context.parsed.y;
            return getCOPColor(value).background;
          },
          borderColor: (context: any) => {
            const value = context.parsed.y;
            return getCOPColor(value).border;
          },
          borderWidth: 1,
        }
      ]
    };
  }, [copData]);

  const chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Coefficient of Performance (COP)',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const value = context.parsed.y;
            let performance = '';
            if (value < 2) performance = 'Poor efficiency';
            else if (value < 3) performance = 'Fair efficiency';
            else if (value < 4) performance = 'Good efficiency';
            else performance = 'Excellent efficiency';
            
            return [`Performance: ${performance}`];
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time Period'
        }
      },
      y: {
        title: {
          display: true,
          text: 'COP (Thermal Energy / Electrical Energy)'
        },
        beginAtZero: true,
        max: Math.max(6, Math.max(...(copData.map(d => d.cop || 0))) * 1.1), // Dynamic max with minimum of 6
        grid: {
          color: (context) => {
            // Add reference lines for performance thresholds
            if (context.tick.value === 2 || context.tick.value === 3 || context.tick.value === 4) {
              return 'rgba(0, 0, 0, 0.2)';
            }
            return 'rgba(0, 0, 0, 0.1)';
          }
        }
      }
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-100 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="text-center py-8">
          <p className="text-red-600 font-medium">Error calculating COP</p>
          <p className="text-sm text-gray-500 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!copData || copData.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="text-center py-8">
          <p className="text-gray-500 font-medium">No COP data available</p>
          <p className="text-sm text-gray-400 mt-1">
            Please select both electrical and thermal sensors to calculate COP
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="mb-4">
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 mr-2 rounded"></div>
            <span>Poor (&lt;2.0)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-500 mr-2 rounded"></div>
            <span>Fair (2.0-3.0)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 mr-2 rounded"></div>
            <span>Good (3.0-4.0)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 mr-2 rounded"></div>
            <span>Excellent (&gt;4.0)</span>
          </div>
        </div>
      </div>
      <div style={{ height: '480px' }}>
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default COPChart;