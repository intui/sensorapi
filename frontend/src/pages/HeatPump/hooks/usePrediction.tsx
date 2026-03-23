import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_WEATHER_FORECAST, GET_ENERGY_PREDICTIONS } from '../../../graphql/queries';
import { TRAIN_PREDICTION_MODEL } from '../../../graphql/mutations';
import type {
  WeatherForecastPoint,
  PredictionResult,
  ModelInfo,
  PredictionHorizon,
} from '../types/prediction.types';

interface UsePredictionParams {
  electricalSensorId: string | null;
  thermalSensorId: string | null;
  locationId: string | null;
  horizon: PredictionHorizon;
}

interface UsePredictionReturn {
  weatherData: WeatherForecastPoint[];
  predictionData: PredictionResult | null;
  weatherLoading: boolean;
  predictionLoading: boolean;
  weatherError: string | null;
  predictionError: string | null;
  isTraining: boolean;
  trainModel: (lookbackDays?: number) => void;
  trainingResult: ModelInfo | null;
  trainingError: string | null;
  refetchPredictions: () => void;
}

export function usePrediction({
  electricalSensorId,
  thermalSensorId,
  locationId,
  horizon,
}: UsePredictionParams): UsePredictionReturn {
  const [trainingResult, setTrainingResult] = useState<ModelInfo | null>(null);
  const [trainingError, setTrainingError] = useState<string | null>(null);

  const hours = horizon === '24h' ? 24 : 96;
  const skip = !locationId;

  const {
    data: weatherRaw,
    loading: weatherLoading,
    error: weatherErr,
  } = useQuery(GET_WEATHER_FORECAST, {
    variables: { locationId, hours },
    skip,
    fetchPolicy: 'cache-and-network',
  });

  const skipPrediction = !electricalSensorId || !thermalSensorId || !locationId;

  const {
    data: predRaw,
    loading: predictionLoading,
    error: predErr,
    refetch: refetchPred,
  } = useQuery(GET_ENERGY_PREDICTIONS, {
    variables: {
      electricalSensorId,
      thermalSensorId,
      locationId,
      hours,
    },
    skip: skipPrediction,
    fetchPolicy: 'cache-and-network',
  });

  const [trainMutation, { loading: isTraining }] = useMutation(TRAIN_PREDICTION_MODEL);

  const trainModel = useCallback(
    (lookbackDays = 90) => {
      if (!electricalSensorId || !thermalSensorId || !locationId) return;
      setTrainingError(null);
      setTrainingResult(null);

      trainMutation({
        variables: {
          input: {
            electricalSensorId,
            thermalSensorId,
            locationId,
            lookbackDays,
          },
        },
      })
        .then((res) => {
          const info = res.data?.trainPredictionModel;
          if (info) {
            setTrainingResult(info);
            // Refetch predictions with the newly trained model
            refetchPred();
          }
        })
        .catch((err: Error) => {
          setTrainingError(err.message || 'Training failed');
        });
    },
    [electricalSensorId, thermalSensorId, locationId, trainMutation, refetchPred],
  );

  const refetchPredictions = useCallback(() => {
    if (!skipPrediction) {
      refetchPred();
    }
  }, [skipPrediction, refetchPred]);

  return {
    weatherData: weatherRaw?.weatherForecast ?? [],
    predictionData: predRaw?.energyPredictions ?? null,
    weatherLoading,
    predictionLoading,
    weatherError: weatherErr?.message ?? null,
    predictionError: predErr?.message ?? null,
    isTraining,
    trainModel,
    trainingResult,
    trainingError,
    refetchPredictions,
  };
}
