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
    console.group('🕒 generateTimePeriods - DEBUG');
    console.log('📅 Input timeRange:', {
        startTime: timeRange.startTime,
        endTime: timeRange.endTime,
        aggregation
    });

    const periods: { start: Date; end: Date; label: string }[] = [];
    const startTime = new Date(timeRange.startTime);
    const endTime = new Date(timeRange.endTime);

    console.log('🌍 Timezone Analysis:', {
        userTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        startTimeLocal: startTime.toLocaleString('en-US', { timeZoneName: 'short' }),
        startTimeUTC: startTime.toISOString(),
        endTimeLocal: endTime.toLocaleString('en-US', { timeZoneName: 'short' }),
        endTimeUTC: endTime.toISOString(),
        timezoneOffset: startTime.getTimezoneOffset() + ' minutes'
    });

    let current = new Date(startTime);
    let periodCount = 0;

    while (current < endTime) {
        periodCount++;
        let periodEnd = new Date(current);
        let label: string;

        console.log(`\n📊 Period ${periodCount}:`);
        console.log('  Start:', {
            iso: current.toISOString(),
            local: current.toLocaleString('en-US', { timeZoneName: 'short' }),
            utc: current.toUTCString()
        });

        switch (aggregation) {
            case 'hour':
                periodEnd.setHours(current.getHours() + 1);
                label = current.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    hour12: true
                });
                console.log('  ⏰ Hour aggregation - adding 1 hour');
                break;
            case 'day':
                periodEnd.setDate(current.getDate() + 1);
                label = current.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
                console.log('  📅 Day aggregation - adding 1 day');
                break;
            case 'month':
                periodEnd.setMonth(current.getMonth() + 1);
                label = current.toLocaleDateString('en-US', {
                    month: 'long',
                    year: 'numeric'
                });
                console.log('  🗓️ Month aggregation - adding 1 month');
                break;
            default:
                periodEnd.setHours(current.getHours() + 1);
                label = current.toISOString();
                console.log('  ⚠️ Default aggregation - adding 1 hour');
        }

        // Don't exceed the end time
        if (periodEnd > endTime) {
            console.log('  ⚠️ Period end exceeds time range, clamping to end time');
            periodEnd = new Date(endTime);
        }

        console.log('  End:', {
            iso: periodEnd.toISOString(),
            local: periodEnd.toLocaleString('en-US', { timeZoneName: 'short' }),
            utc: periodEnd.toUTCString()
        });
        console.log('  Label:', label);
        console.log('  Duration (ms):', periodEnd.getTime() - current.getTime());
        console.log('  Duration (hours):', (periodEnd.getTime() - current.getTime()) / (1000 * 60 * 60));

        periods.push({
            start: new Date(current),
            end: new Date(periodEnd),
            label
        });

        current = new Date(periodEnd);

        // Safety check to prevent infinite loops
        if (periodCount > 1000) {
            console.error('⚠️ SAFETY BREAK: Too many periods generated, stopping to prevent infinite loop');
            break;
        }
    }

    console.log('\n📈 Summary:', {
        totalPeriods: periods.length,
        firstPeriod: periods[0] ? {
            start: periods[0].start.toISOString(),
            end: periods[0].end.toISOString(),
            label: periods[0].label
        } : null,
        lastPeriod: periods[periods.length - 1] ? {
            start: periods[periods.length - 1].start.toISOString(),
            end: periods[periods.length - 1].end.toISOString(),
            label: periods[periods.length - 1].label
        } : null
    });

    console.groupEnd();
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
        if (!timeRange.startTime || !timeRange.endTime) {
            console.log('🚫 generateTimePeriods skipped: missing timeRange', { timeRange });
            return [];
        }
        console.log('🚀 Generating time periods...', { timeRange, aggregation });
        const periods = generateTimePeriods(timeRange, aggregation);
        console.log('✅ Time periods generated:', periods.length);
        return periods;
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
                        const [
                            electricalStartResult,
                            electricalEndResult,
                            thermalStartResult,
                            thermalEndResult
                        ] = await Promise.all([
                            getReadingsAround({
                                variables: {
                                    sensorId: electricalSensorId,
                                    targetTime: period.start.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            }),
                            getReadingsAround({
                                variables: {
                                    sensorId: electricalSensorId,
                                    targetTime: period.end.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            }),
                            getReadingsAround({
                                variables: {
                                    sensorId: thermalSensorId,
                                    targetTime: period.start.toISOString(),
                                    before: 1,
                                    after: 1
                                }
                            }),
                            getReadingsAround({
                                variables: {
                                    sensorId: thermalSensorId,
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

                        console.log(`🔋 Energy Calculation for ${period.label}:`, {
                            electrical: {
                                start: electricalStart,
                                end: electricalEnd,
                                energy: electricalEnergy,
                                unit: 'kWh'
                            },
                            thermal: {
                                start: thermalStart,
                                end: thermalEnd,
                                energy: thermalEnergy,
                                unit: 'kWh'
                            },
                            cop: {
                                value: cop,
                                calculation: `${thermalEnergy} / ${electricalEnergy} = ${cop}`,
                                valid: cop !== null,
                                efficiency: cop ? (
                                    cop < 2 ? 'Poor' :
                                        cop < 3 ? 'Fair' :
                                            cop < 4 ? 'Good' : 'Excellent'
                                ) : 'N/A'
                            }
                        });

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

                console.group('📊 COP Calculation Summary');
                console.log('📈 Final Results:', {
                    totalCalculations: copCalculations.length,
                    validCOPs: copCalculations.filter(c => c.cop !== null).length,
                    invalidCOPs: copCalculations.filter(c => c.cop === null).length,
                    averageCOP: copCalculations.length > 0 ?
                        copCalculations.filter(c => c.cop !== null).reduce((sum, c) => sum + (c.cop || 0), 0) /
                        copCalculations.filter(c => c.cop !== null).length : 0,
                    totalElectricalEnergy: copCalculations.reduce((sum, c) => sum + c.electricalEnergy, 0),
                    totalThermalEnergy: copCalculations.reduce((sum, c) => sum + c.thermalEnergy, 0),
                    overallCOP: copCalculations.reduce((sum, c) => sum + c.electricalEnergy, 0) > 0 ?
                        copCalculations.reduce((sum, c) => sum + c.thermalEnergy, 0) /
                        copCalculations.reduce((sum, c) => sum + c.electricalEnergy, 0) : null
                });

                if (copCalculations.length > 0) {
                    console.table(copCalculations.map(calc => ({
                        period: calc.timestamp,
                        electrical_kWh: calc.electricalEnergy.toFixed(3),
                        thermal_kWh: calc.thermalEnergy.toFixed(3),
                        cop: calc.cop ? calc.cop.toFixed(2) : 'N/A',
                        efficiency: calc.cop ? (
                            calc.cop < 2 ? 'Poor' :
                                calc.cop < 3 ? 'Fair' :
                                    calc.cop < 4 ? 'Good' : 'Excellent'
                        ) : 'N/A'
                    })));
                }
                console.groupEnd();

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