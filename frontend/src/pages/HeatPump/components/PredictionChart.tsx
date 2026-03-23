import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from 'chart.js';
import type { EnergyPredictionPoint } from '../types/prediction.types';
import type { PredictionHorizon } from '../types/prediction.types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend
);

interface PredictionChartProps {
  predictions: EnergyPredictionPoint[];
  horizon: PredictionHorizon;
  isLoading?: boolean;
  error?: string | null;
}

const formatLabel = (ts: string, horizon: PredictionHorizon): string => {
  const dt = new Date(ts);
  if (horizon === '24h') {
    return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  }
  return dt.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', hour12: false });
};

const PredictionChart: React.FC<PredictionChartProps> = ({
  predictions,
  horizon,
  isLoading = false,
  error = null,
}) => {
  const chartData = useMemo(() => {
    if (!predictions.length) return null;

    const labels = predictions.map(p => formatLabel(p.timestamp, horizon));

    return {
      labels,
      datasets: [
        // Electrical confidence band
        {
          label: 'Electrical 95% CI',
          data: predictions.map(p => p.confidenceHighElectrical),
          borderColor: 'transparent',
          backgroundColor: 'rgba(59, 130, 246, 0.08)',
          fill: '+1',
          pointRadius: 0,
          tension: 0.4,
          order: 10,
        },
        {
          label: '_elec_low',
          data: predictions.map(p => p.confidenceLowElectrical),
          borderColor: 'transparent',
          backgroundColor: 'rgba(59, 130, 246, 0.08)',
          fill: false,
          pointRadius: 0,
          tension: 0.4,
          order: 11,
        },
        // Thermal confidence band
        {
          label: 'Thermal 95% CI',
          data: predictions.map(p => p.confidenceHighThermal),
          borderColor: 'transparent',
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          fill: '+1',
          pointRadius: 0,
          tension: 0.4,
          order: 12,
        },
        {
          label: '_therm_low',
          data: predictions.map(p => p.confidenceLowThermal),
          borderColor: 'transparent',
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          fill: false,
          pointRadius: 0,
          tension: 0.4,
          order: 13,
        },
        // Main lines
        {
          label: 'Predicted Electrical (kWh)',
          data: predictions.map(p => p.predictedElectricalKwh),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 2.5,
          pointRadius: horizon === '24h' ? 3 : 1,
          pointHoverRadius: 6,
          tension: 0.4,
          fill: false,
          order: 1,
        },
        {
          label: 'Predicted Thermal (kWh)',
          data: predictions.map(p => p.predictedThermalKwh),
          borderColor: 'rgb(245, 158, 11)',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          borderWidth: 2.5,
          pointRadius: horizon === '24h' ? 3 : 1,
          pointHoverRadius: 6,
          tension: 0.4,
          fill: false,
          order: 2,
        },
        // Temperature on secondary axis
        {
          label: 'Temperature (°C)',
          data: predictions.map(p => p.temperature),
          borderColor: 'rgba(139, 92, 246, 0.6)',
          backgroundColor: 'rgba(139, 92, 246, 0.05)',
          borderWidth: 1.5,
          borderDash: [6, 3],
          pointRadius: 0,
          tension: 0.4,
          fill: false,
          yAxisID: 'y1',
          order: 5,
        },
      ],
    };
  }, [predictions, horizon]);

  const chartOptions: ChartOptions<'line'> = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          filter: item => !item.text.startsWith('_'),
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 16,
          font: { size: 12 },
        },
      },
      title: {
        display: true,
        text: `Energy Prediction — Next ${horizon === '24h' ? '24 Hours' : '96 Hours (4 Days)'}`,
        font: { size: 16, weight: 'bold' },
        padding: { bottom: 16 },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleFont: { size: 13 },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          afterBody: (ctx) => {
            const idx = ctx[0]?.dataIndex;
            if (idx !== undefined && predictions[idx]) {
              const p = predictions[idx];
              const lines = [];
              if (p.predictedCop !== null) {
                lines.push(`Predicted COP: ${p.predictedCop}`);
              }
              return lines;
            }
            return [];
          },
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'Time' },
        ticks: {
          maxTicksLimit: horizon === '24h' ? 12 : 16,
          maxRotation: 45,
          font: { size: 11 },
        },
        grid: { display: false },
      },
      y: {
        position: 'left',
        title: { display: true, text: 'Energy (kWh)' },
        beginAtZero: true,
        grid: { color: 'rgba(0,0,0,0.05)' },
      },
      y1: {
        position: 'right',
        title: { display: true, text: 'Temperature (°C)' },
        grid: { drawOnChartArea: false },
      },
    },
    animation: {
      duration: 800,
      easing: 'easeOutQuart',
    },
  }), [horizon, predictions]);

  if (isLoading) {
    return (
      <div style={{
        background: '#fff',
        borderRadius: 12,
        padding: 24,
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      }}>
        <div style={{
          height: 350,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 12,
        }}>
          <div style={{
            width: 40,
            height: 40,
            border: '3px solid #e2e8f0',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }} />
          <span style={{ color: '#64748b', fontSize: 14 }}>Loading predictions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        background: '#fff',
        borderRadius: 12,
        padding: 24,
        border: '1px solid #e2e8f0',
      }}>
        <div style={{
          background: '#fef2f2',
          borderRadius: 8,
          padding: 16,
          border: '1px solid #fecaca',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🤖</div>
          <p style={{ color: '#b91c1c', fontWeight: 600, marginBottom: 4 }}>
            Prediction not available
          </p>
          <p style={{ color: '#dc2626', fontSize: 13 }}>{error}</p>
        </div>
      </div>
    );
  }

  if (!chartData || predictions.length === 0) {
    return (
      <div style={{
        background: '#fff',
        borderRadius: 12,
        padding: 24,
        border: '1px solid #e2e8f0',
      }}>
        <div style={{
          height: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#94a3b8',
          fontSize: 14,
        }}>
          Select sensors and train a model to see energy predictions
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: '#fff',
      borderRadius: 12,
      padding: 24,
      border: '1px solid #e2e8f0',
      boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    }}>
      <div style={{ height: 380 }}>
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default PredictionChart;
