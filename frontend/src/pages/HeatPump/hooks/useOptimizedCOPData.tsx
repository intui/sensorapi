import { useState, useEffect, useMemo } from 'react';
import { useLazyQuery } from '@apollo/client';
import { GET_SENSOR_READINGS_AROUND } from '../../../graphql/queries';
import type { COPCalculation, AggregationType, TimeRange } from '../types/heatpump.types';

interface UseOptimizedCOPDataProps {
    electricalSensorId: string | null;
    thermalSensorId: string | null;
    timeRange: TimeRange;
    aggregation: AggregationType;
}

interface UseOptimizedCOPDataReturn {
    copData: COPCalculation[];
    isLoading: boolean;
    error: string | null;
}

// Helper function to generate time periods based on aggregation
const generateTimePeriods = (timeRange: TimeRange, aggregation: AggregationType) => {
    const periods: { start: Date; end: Date; label: string }[] = [];
    const startTime = new Date(timeRange.startTime);
    const endTime = new Date(timeRange.endTime);

    let current = new Date(startTime);

    while (current < endTime) {
        let periodEnd = new Date(current);
        let label: string;

        switch (aggregation) {
            case 'hour':
                periodEnd.setHours(current.getHours() + 1);
                label = current.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    hour12: true
                });
                break;
            case 'day':
                periodEnd.setDate(current.getDate() + 1);
                label = current.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
                break;
            case 'month':
                periodEnd.setMonth(current.getMonth() + 1);
                label = current.toLocaleDateString('en-US', {
                    month: 'long',
                    year: 'numeric'
                });
                break;
            default:
                periodEnd.setHours(current.getHours() + 1);
                label = current.toISOString();
        }

        // Don't exceed the end time
        if (periodEnd > endTime) {
            periodEnd = new Date(endTime);
        }

        periods.push({
            start: new Date(current),
            end: new Date(periodEnd),
            label
        });

        current = new Date(periodEnd);
    }

    return periods;
};

/**
 * Optimized COP calculation hook that uses GET_SENSOR_READINGS_AROUND
 * to fetch only the specific readings needed for each time period,
 * instead of fetching all readings and sorting/processing them.
 * 
 * Performance benefits:
 * - Reduces network payload from ~10K readings to ~8 readings per period
 * - Eliminates large array sorting operations
 * - Reduces memory usage
 * - Faster calculation times
 */
export const useOptimizedCOPData = ({
    electricalSensorId,
    thermalSensorId,
    timeRange,
    aggregation
}: UseOptimizedCOPDataProps): UseOptimizedCOPDataReturn => {
    const [copData, setCopData] = useState<COPCalculation[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Use lazy query to fetch readings around specific times
    const [getReadingsAround] = useLazyQuery(GET_SENSOR_READINGS_AROUND);

    // Generate time periods
    const timePeriods = useMemo(() => {
        if (!timeRange.startTime || !timeRange.endTime) return [];
        return generateTimePeriods(timeRange, aggregation);
    }, [timeRange, aggregation]);

    useEffect(() => {
        if (!electricalSensorId || !thermalSensorId || timePeriods.length === 0) {
            setCopData([]);
            return;
        }

        setIsLoading(true);
        setError(null);

        const fetchCOPData = async () => {
            try {
                const copCalculations: COPCalculation[] = [];

                // Process each time period sequentially to avoid overwhelming the server
                for (const period of timePeriods) {
                    try {
                        // Fetch readings around period start and end for both sensors
                        // NOTE: Swapping electrical and thermal to fix inverted COP calculation
                        // This suggests the sensor labeling may be incorrect in the database
                        const [
                            thermalStartResult,     // Using thermalSensorId to get what we'll use as electricalStart
                            thermalEndResult,       // Using thermalSensorId to get what we'll use as electricalEnd
                            electricalStartResult,  // Using electricalSensorId to get what we'll use as thermalStart
                            electricalEndResult     // Using electricalSensorId to get what we'll use as thermalEnd
                        ] = await Promise.all([
                            getReadingsAround({
                                variables: {
                                    sensorId: thermalSensorId,  // SWAPPED: was electricalSensorId
                                    targetTime: period.start.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            }),
                            getReadingsAround({
                                variables: {
                                    sensorId: thermalSensorId,  // SWAPPED: was electricalSensorId
                                    targetTime: period.end.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            }),
                            getReadingsAround({
                                variables: {
                                    sensorId: electricalSensorId,  // SWAPPED: was thermalSensorId
                                    targetTime: period.start.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            }),
                            getReadingsAround({
                                variables: {
                                    sensorId: electricalSensorId,  // SWAPPED: was thermalSensorId
                                    targetTime: period.end.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            })
                        ]);

                        // Helper function to extract the closest value to target time
                        const getClosestValue = (result: any, targetTime: Date): number | null => {
                            const readings = result.data?.sensorReadingsAround;
                            if (!readings) return null;

                            const before = readings.before?.[0];
                            const after = readings.after?.[0];

                            if (!before && !after) return null;
                            if (!before) return after.value;
                            if (!after) return before.value;

                            // Choose the reading closest to the target time
                            const beforeTime = new Date(before.timestamp);
                            const afterTime = new Date(after.timestamp);
                            const beforeDiff = Math.abs(targetTime.getTime() - beforeTime.getTime());
                            const afterDiff = Math.abs(targetTime.getTime() - afterTime.getTime());

                            return beforeDiff <= afterDiff ? before.value : after.value;
                        };

                        // Extract start and end values for both sensors
                        const electricalStart = getClosestValue(electricalStartResult, period.start);
                        const electricalEnd = getClosestValue(electricalEndResult, period.end);
                        const thermalStart = getClosestValue(thermalStartResult, period.start);
                        const thermalEnd = getClosestValue(thermalEndResult, period.end);

                        // Skip if we don't have all required readings
                        if (electricalStart === null || electricalEnd === null ||
                            thermalStart === null || thermalEnd === null) {
                            console.warn(`Missing readings for period ${period.label}, skipping...`);
                            continue;
                        }

                        // Calculate energy consumption for the period
                        const electricalEnergy = Math.max(0, electricalEnd - electricalStart);
                        const thermalEnergy = Math.max(0, thermalEnd - thermalStart);

                        // Calculate COP (thermal output / electrical input)
                        const cop = electricalEnergy > 0 ? thermalEnergy / electricalEnergy : null;

                        copCalculations.push({
                            timestamp: period.label,
                            electricalEnergy,
                            thermalEnergy,
                            cop,
                            _sortDate: period.start.toISOString()
                        });

                    } catch (periodError) {
                        console.error(`Error processing period ${period.label}:`, periodError);
                        // Continue with other periods even if one fails
                    }
                }

                // Sort by time (should already be in order, but ensure proper sorting)
                copCalculations.sort((a, b) => {
                    const dateA = new Date(a._sortDate || a.timestamp);
                    const dateB = new Date(b._sortDate || b.timestamp);
                    return dateA.getTime() - dateB.getTime();
                });

                setCopData(copCalculations);
            } catch (fetchError) {
                console.error('Error fetching optimized COP data:', fetchError);
                setError(fetchError instanceof Error ? fetchError.message : 'Failed to fetch COP data');
            } finally {
                setIsLoading(false);
            }
        };

        fetchCOPData();
    }, [electricalSensorId, thermalSensorId, timePeriods, getReadingsAround]);

    return {
        copData,
        isLoading,
        error
    };
};