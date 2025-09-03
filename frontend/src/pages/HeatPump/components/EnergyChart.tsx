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

interface EnergyChartProps {
  copData: COPCalculation[];
  isLoading?: boolean;
  error?: string | null;
}

const EnergyChart: React.FC<EnergyChartProps> = ({
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

    return {
      labels: copData.map(item => item.timestamp),
      datasets: [
        {
          label: 'Electrical Energy (kWh)',
          data: copData.map(item => item.electricalEnergy),
          backgroundColor: 'rgba(59, 130, 246, 0.8)', // blue
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
        },
        {
          label: 'Thermal Energy (kWh)',
          data: copData.map(item => item.thermalEnergy),
          backgroundColor: 'rgba(245, 158, 11, 0.8)', // orange
          borderColor: 'rgb(245, 158, 11)',
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
        text: 'Energy Consumption vs Production',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          afterBody: (context) => {
            if (context.length >= 2) {
              const electricalValue = context.find(item => item.datasetIndex === 0)?.parsed.y || 0;
              const thermalValue = context.find(item => item.datasetIndex === 1)?.parsed.y || 0;
              const cop = electricalValue > 0 ? (thermalValue / electricalValue).toFixed(2) : 'N/A';
              return [`COP: ${cop}`];
            }
            return [];
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
          text: 'Energy (kWh)'
        },
        beginAtZero: true
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
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
          <p className="text-red-600 font-medium">Error loading energy data</p>
          <p className="text-sm text-gray-500 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!copData || copData.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="text-center py-8">
          <p className="text-gray-500 font-medium">No energy data available</p>
          <p className="text-sm text-gray-400 mt-1">
            Please select both electrical and thermal sensors to view energy data
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div style={{ height: '480px' }}>
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default EnergyChart;