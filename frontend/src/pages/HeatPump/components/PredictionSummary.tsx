import React, { useState } from 'react';
import type { PredictionResult, PredictionHorizon, ModelInfo } from '../types/prediction.types';

interface PredictionSummaryProps {
  prediction: PredictionResult | null;
  horizon: PredictionHorizon;
  onHorizonChange: (h: PredictionHorizon) => void;
  onTrainModel: (lookbackDays: number) => void;
  isTraining: boolean;
  trainingResult: ModelInfo | null;
  trainingError: string | null;
  predictionLoading: boolean;
  canPredict: boolean;
}

const PredictionSummary: React.FC<PredictionSummaryProps> = ({
  prediction,
  horizon,
  onHorizonChange,
  onTrainModel,
  isTraining,
  trainingResult,
  trainingError,
  predictionLoading,
  canPredict,
}) => {
  const [lookbackDays, setLookbackDays] = useState(90);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const modelInfo = prediction?.modelInfo ?? trainingResult;

  const copRating = (cop: number | null): { label: string; color: string; emoji: string } => {
    if (cop === null) return { label: 'N/A', color: '#94a3b8', emoji: '❓' };
    if (cop >= 4.0) return { label: 'Excellent', color: '#16a34a', emoji: '🟢' };
    if (cop >= 3.0) return { label: 'Good', color: '#65a30d', emoji: '🟡' };
    if (cop >= 2.0) return { label: 'Fair', color: '#d97706', emoji: '🟠' };
    return { label: 'Poor', color: '#dc2626', emoji: '🔴' };
  };

  const r2Color = (r2: number): string => {
    if (r2 >= 0.8) return '#16a34a';
    if (r2 >= 0.5) return '#d97706';
    return '#dc2626';
  };

  const rating = prediction ? copRating(prediction.averageCop) : copRating(null);

  return (
    <div style={{
      background: '#fff',
      borderRadius: 12,
      padding: 24,
      border: '1px solid #e2e8f0',
      boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    }}>
      {/* Header with horizon slider and train button */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 20,
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 20 }}>🔮</span>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: '#1e293b' }}>
            Energy Prediction
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          {/* Horizon toggle */}
          <div style={{
            display: 'flex',
            borderRadius: 8,
            overflow: 'hidden',
            border: '1px solid #e2e8f0',
          }}>
            {(['24h', '96h'] as PredictionHorizon[]).map(h => (
              <button
                key={h}
                onClick={() => onHorizonChange(h)}
                style={{
                  padding: '6px 16px',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: 13,
                  fontWeight: 600,
                  background: horizon === h ? '#3b82f6' : '#fff',
                  color: horizon === h ? '#fff' : '#64748b',
                  transition: 'all 0.2s ease',
                }}
              >
                {h === '24h' ? '24 Hours' : '96 Hours'}
              </button>
            ))}
          </div>

          {/* Train button */}
          <button
            onClick={() => onTrainModel(lookbackDays)}
            disabled={isTraining || !canPredict}
            style={{
              padding: '6px 16px',
              borderRadius: 8,
              border: 'none',
              cursor: isTraining || !canPredict ? 'not-allowed' : 'pointer',
              fontSize: 13,
              fontWeight: 600,
              background: isTraining
                ? 'linear-gradient(135deg, #93c5fd, #60a5fa)'
                : 'linear-gradient(135deg, #3b82f6, #2563eb)',
              color: '#fff',
              transition: 'all 0.3s ease',
              opacity: !canPredict ? 0.5 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              boxShadow: '0 2px 8px rgba(59,130,246,0.3)',
            }}
          >
            {isTraining ? (
              <>
                <span style={{
                  display: 'inline-block',
                  width: 14,
                  height: 14,
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTopColor: '#fff',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite',
                }} />
                Training...
              </>
            ) : (
              <>🧠 Train Model</>
            )}
          </button>

          {/* Advanced toggle */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              padding: '6px 12px',
              borderRadius: 8,
              border: '1px solid #e2e8f0',
              cursor: 'pointer',
              fontSize: 12,
              background: showAdvanced ? '#f1f5f9' : '#fff',
              color: '#64748b',
              transition: 'all 0.2s ease',
            }}
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* Advanced settings panel */}
      {showAdvanced && (
        <div style={{
          background: '#f8fafc',
          borderRadius: 8,
          padding: 16,
          marginBottom: 16,
          border: '1px solid #e2e8f0',
          animation: 'slideDown 0.2s ease',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
            <label style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 13,
              color: '#475569',
              margin: 0,
            }}>
              Training lookback:
              <input
                type="range"
                min={14}
                max={365}
                step={7}
                value={lookbackDays}
                onChange={e => setLookbackDays(Number(e.target.value))}
                style={{
                  width: 120,
                  accentColor: '#3b82f6',
                  cursor: 'pointer',
                }}
              />
              <span style={{
                fontWeight: 700,
                color: '#1e293b',
                minWidth: 60,
              }}>
                {lookbackDays} days
              </span>
            </label>
          </div>
        </div>
      )}

      {/* Training result / error */}
      {trainingResult && !trainingError && (
        <div style={{
          background: '#f0fdf4',
          borderRadius: 8,
          padding: '10px 16px',
          marginBottom: 16,
          border: '1px solid #bbf7d0',
          fontSize: 13,
          color: '#166534',
          animation: 'fadeIn 0.5s ease',
        }}>
          ✅ Model trained successfully! {trainingResult.trainingSamples} samples, 
          R²(electrical): {(trainingResult.r2Electrical * 100).toFixed(1)}%, 
          R²(thermal): {(trainingResult.r2Thermal * 100).toFixed(1)}%
        </div>
      )}
      {trainingError && (
        <div style={{
          background: '#fef2f2',
          borderRadius: 8,
          padding: '10px 16px',
          marginBottom: 16,
          border: '1px solid #fecaca',
          fontSize: 13,
          color: '#b91c1c',
          animation: 'fadeIn 0.5s ease',
        }}>
          ❌ Training failed: {trainingError}
        </div>
      )}

      {/* Summary cards */}
      {predictionLoading ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 12,
        }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} style={{
              borderRadius: 10,
              padding: 16,
              height: 90,
              background: '#f1f5f9',
              animation: 'pulse 1.5s ease-in-out infinite',
              animationDelay: `${i * 0.15}s`,
            }} />
          ))}
        </div>
      ) : prediction ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: 12,
        }}>
          {/* Predicted electrical */}
          <div style={{
            background: 'linear-gradient(135deg, #eff6ff, #dbeafe)',
            borderRadius: 10,
            padding: 16,
            transition: 'transform 0.2s ease',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1.02)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1)'; }}
          >
            <div style={{ fontSize: 12, fontWeight: 600, color: '#2563eb', marginBottom: 4 }}>
              ⚡ Predicted Electrical
            </div>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#1e40af' }}>
              {prediction.totalElectricalKwh.toFixed(1)}
            </div>
            <div style={{ fontSize: 11, color: '#3b82f6' }}>kWh ({horizon})</div>
          </div>

          {/* Predicted thermal */}
          <div style={{
            background: 'linear-gradient(135deg, #fff7ed, #fed7aa)',
            borderRadius: 10,
            padding: 16,
            transition: 'transform 0.2s ease',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1.02)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1)'; }}
          >
            <div style={{ fontSize: 12, fontWeight: 600, color: '#d97706', marginBottom: 4 }}>
              🔥 Predicted Thermal
            </div>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#92400e' }}>
              {prediction.totalThermalKwh.toFixed(1)}
            </div>
            <div style={{ fontSize: 11, color: '#d97706' }}>kWh ({horizon})</div>
          </div>

          {/* Average COP */}
          <div style={{
            background: `linear-gradient(135deg, ${rating.color}11, ${rating.color}22)`,
            borderRadius: 10,
            padding: 16,
            transition: 'transform 0.2s ease',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1.02)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1)'; }}
          >
            <div style={{ fontSize: 12, fontWeight: 600, color: rating.color, marginBottom: 4 }}>
              {rating.emoji} Predicted COP
            </div>
            <div style={{ fontSize: 24, fontWeight: 700, color: rating.color }}>
              {prediction.averageCop?.toFixed(2) ?? 'N/A'}
            </div>
            <div style={{ fontSize: 11, color: rating.color }}>{rating.label}</div>
          </div>

          {/* Model accuracy */}
          {modelInfo && (
            <div style={{
              background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)',
              borderRadius: 10,
              padding: 16,
              transition: 'transform 0.2s ease',
            }}
            onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1.02)'; }}
            onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.transform = 'scale(1)'; }}
            >
              <div style={{ fontSize: 12, fontWeight: 600, color: '#475569', marginBottom: 4 }}>
                🧠 Model Accuracy
              </div>
              <div style={{ fontSize: 13, color: '#1e293b' }}>
                <span style={{ fontWeight: 700, color: r2Color(modelInfo.r2Electrical) }}>
                  {(modelInfo.r2Electrical * 100).toFixed(0)}%
                </span>
                <span style={{ color: '#94a3b8' }}> elec · </span>
                <span style={{ fontWeight: 700, color: r2Color(modelInfo.r2Thermal) }}>
                  {(modelInfo.r2Thermal * 100).toFixed(0)}%
                </span>
                <span style={{ color: '#94a3b8' }}> therm</span>
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                {modelInfo.trainingSamples} training samples
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '24px 16px',
          color: '#94a3b8',
          fontSize: 14,
        }}>
          {canPredict ? (
            <>
              <div style={{ fontSize: 32, marginBottom: 8 }}>🧠</div>
              <p style={{ margin: 0 }}>Click <strong>Train Model</strong> to create predictions from your historical data.</p>
            </>
          ) : (
            <>
              <div style={{ fontSize: 32, marginBottom: 8 }}>👆</div>
              <p style={{ margin: 0 }}>Select both sensors above to enable predictions.</p>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default PredictionSummary;
