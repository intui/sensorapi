import React from 'react';
import type { WeatherForecastPoint } from '../types/prediction.types';

interface WeatherPreviewProps {
  data: WeatherForecastPoint[];
  loading?: boolean;
  error?: string | null;
}

const weatherIcon = (temp: number, cloud: number | null, precip: number | null): string => {
  if (precip && precip > 1) return '🌧️';
  if (precip && precip > 0) return '🌦️';
  if (cloud !== null && cloud > 70) return '☁️';
  if (cloud !== null && cloud > 30) return '⛅';
  if (temp < 0) return '❄️';
  if (temp > 25) return '☀️';
  return '🌤️';
};

const WeatherPreview: React.FC<WeatherPreviewProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #e0f2fe, #f0f9ff)',
        borderRadius: 12,
        padding: '16px 20px',
        border: '1px solid #bae6fd',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <span style={{ fontSize: 18 }}>🌤️</span>
          <span style={{ fontWeight: 600, color: '#0369a1' }}>Weather Forecast</span>
        </div>
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} style={{
              minWidth: 56,
              height: 72,
              borderRadius: 10,
              background: 'rgba(255,255,255,0.5)',
              animation: 'pulse 1.5s ease-in-out infinite',
              animationDelay: `${i * 0.1}s`,
            }} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        background: '#fef2f2',
        borderRadius: 12,
        padding: '12px 20px',
        border: '1px solid #fecaca',
        color: '#b91c1c',
        fontSize: 14,
      }}>
        ⚠️ Weather data unavailable: {error}
      </div>
    );
  }

  if (!data || data.length === 0) return null;

  // Sample every 3 hours for the strip
  const sampled = data.filter((_, i) => i % 3 === 0).slice(0, 16);
  const minTemp = Math.min(...sampled.map(d => d.temperature));
  const maxTemp = Math.max(...sampled.map(d => d.temperature));
  const tempRange = maxTemp - minTemp || 1;

  return (
    <div style={{
      background: 'linear-gradient(135deg, #e0f2fe, #f0f9ff)',
      borderRadius: 12,
      padding: '16px 20px',
      border: '1px solid #bae6fd',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 18 }}>🌤️</span>
          <span style={{ fontWeight: 600, color: '#0369a1', fontSize: 14 }}>Weather Forecast</span>
        </div>
        <span style={{ fontSize: 12, color: '#64748b' }}>
          {minTemp.toFixed(0)}°C – {maxTemp.toFixed(0)}°C
        </span>
      </div>

      <div style={{
        display: 'flex',
        gap: 6,
        overflowX: 'auto',
        paddingBottom: 4,
        scrollbarWidth: 'thin',
      }}>
        {sampled.map((point, idx) => {
          const dt = new Date(point.timestamp);
          const timeStr = dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
          const dateStr = dt.toLocaleDateString([], { weekday: 'short' });
          const normalizedTemp = (point.temperature - minTemp) / tempRange;

          // Interpolate color: blue (cold) → yellow → red (hot)
          const r = Math.round(normalizedTemp > 0.5 ? 255 : normalizedTemp * 2 * 255);
          const g = Math.round(normalizedTemp < 0.5 ? normalizedTemp * 2 * 200 : (1 - normalizedTemp) * 2 * 200);
          const b = Math.round(normalizedTemp < 0.5 ? 200 - normalizedTemp * 2 * 200 : 0);

          return (
            <div
              key={idx}
              style={{
                minWidth: 60,
                padding: '8px 4px',
                borderRadius: 10,
                background: 'rgba(255,255,255,0.7)',
                backdropFilter: 'blur(4px)',
                textAlign: 'center',
                cursor: 'default',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                flexShrink: 0,
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)';
                (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
                (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
              }}
              title={`${point.temperature}°C, ${point.humidity ?? '-'}% humidity, ${point.windSpeed ?? '-'} km/h wind`}
            >
              <div style={{ fontSize: 10, color: '#64748b', marginBottom: 2 }}>{dateStr}</div>
              <div style={{ fontSize: 10, color: '#94a3b8', marginBottom: 4 }}>{timeStr}</div>
              <div style={{ fontSize: 18, marginBottom: 4 }}>
                {weatherIcon(point.temperature, point.cloudCover, point.precipitation)}
              </div>
              <div style={{
                fontSize: 13,
                fontWeight: 700,
                color: `rgb(${r}, ${g}, ${b})`,
              }}>
                {point.temperature.toFixed(0)}°
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WeatherPreview;
