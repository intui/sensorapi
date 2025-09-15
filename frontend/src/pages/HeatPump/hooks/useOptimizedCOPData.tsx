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

    // Helper function to align date to period boundary
    const alignToPeriodStart = (date: Date, aggregationType: AggregationType): Date => {
        const aligned = new Date(date);
        switch (aggregationType) {
            case 'hour':
                // Align to start of hour (HH:00:00.000)
                aligned.setMinutes(0, 0, 0);
                break;
            case 'day':
                // Align to start of day (00:00:00.000)
                aligned.setHours(0, 0, 0, 0);
                break;
            case 'month':
                // Align to start of month (1st day, 00:00:00.000)
                aligned.setDate(1);
                aligned.setHours(0, 0, 0, 0);
                break;
        }
        return aligned;
    };

    // Start from the aligned boundary that includes the start time
    let current = alignToPeriodStart(startTime, aggregation);

    // If the aligned start is after our actual start time, go back one period
    if (current > startTime) {
        switch (aggregation) {
            case 'hour':
                current.setHours(current.getHours() - 1);
                break;
            case 'day':
                current.setDate(current.getDate() - 1);
                break;
            case 'month':
                current.setMonth(current.getMonth() - 1);
                break;
        }
    }

    console.log('📐 Boundary Alignment:', {
        originalStart: startTime.toISOString(),
        alignedStart: current.toISOString(),
        aggregation
    });

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
                // End of hour period (next hour start)
                periodEnd.setHours(current.getHours() + 1);
                label = current.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    hour12: true
                });
                console.log('  ⏰ Hour aggregation - full hour boundary');
                break;
            case 'day':
                // End of day period (next day start at midnight)
                periodEnd.setDate(current.getDate() + 1);
                label = current.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
                console.log('  📅 Day aggregation - full calendar day (midnight to midnight)');
                break;
            case 'month':
                // End of month period (next month start)
                periodEnd.setMonth(current.getMonth() + 1);
                label = current.toLocaleDateString('en-US', {
                    month: 'long',
                    year: 'numeric'
                });
                console.log('  🗓️ Month aggregation - full calendar month');
                break;
            default:
                periodEnd.setHours(current.getHours() + 1);
                label = current.toISOString();
                console.log('  ⚠️ Default aggregation - hour boundary');
        }

        console.log('  End:', {
            iso: periodEnd.toISOString(),
            local: periodEnd.toLocaleString('en-US', { timeZoneName: 'short' }),
            utc: periodEnd.toUTCString()
        });
        console.log('  Label:', label);
        console.log('  Duration (ms):', periodEnd.getTime() - current.getTime());
        console.log('  Duration (hours):', (periodEnd.getTime() - current.getTime()) / (1000 * 60 * 60));

        // Validate period boundaries
        const isProperBoundary = (() => {
            switch (aggregation) {
                case 'hour':
                    return current.getMinutes() === 0 && current.getSeconds() === 0 && current.getMilliseconds() === 0;
                case 'day':
                    return current.getHours() === 0 && current.getMinutes() === 0 && current.getSeconds() === 0 && current.getMilliseconds() === 0;
                case 'month':
                    return current.getDate() === 1 && current.getHours() === 0 && current.getMinutes() === 0 && current.getSeconds() === 0 && current.getMilliseconds() === 0;
                default:
                    return true;
            }
        })();

        console.log('  ✅ Proper boundary alignment:', isProperBoundary);

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
        aggregationType: aggregation,
        boundaryAlignment: aggregation === 'day' ? 'midnight-to-midnight' :
            aggregation === 'hour' ? 'hour-to-hour' :
                aggregation === 'month' ? 'month-to-month' : 'custom',
        firstPeriod: periods[0] ? {
            start: periods[0].start.toISOString(),
            end: periods[0].end.toISOString(),
            label: periods[0].label,
            isProperBoundary: aggregation === 'day' ?
                periods[0].start.getHours() === 0 && periods[0].start.getMinutes() === 0 :
                aggregation === 'hour' ?
                    periods[0].start.getMinutes() === 0 && periods[0].start.getSeconds() === 0 :
                    true
        } : null,
        lastPeriod: periods[periods.length - 1] ? {
            start: periods[periods.length - 1].start.toISOString(),
            end: periods[periods.length - 1].end.toISOString(),
            label: periods[periods.length - 1].label,
            isProperBoundary: aggregation === 'day' ?
                periods[periods.length - 1].start.getHours() === 0 && periods[periods.length - 1].start.getMinutes() === 0 :
                aggregation === 'hour' ?
                    periods[periods.length - 1].start.getMinutes() === 0 && periods[periods.length - 1].start.getSeconds() === 0 :
                    true
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
                        const electricalEnergyRaw = electricalEnd - electricalStart;
                        const thermalEnergyRaw = thermalEnd - thermalStart;

                        // Round to 3 decimal places to handle floating-point precision issues
                        // and apply a minimum threshold to filter out noise
                        const ENERGY_PRECISION = 3;
                        const MIN_ENERGY_THRESHOLD = 0.001; // 1 Wh minimum

                        const electricalEnergy = Math.round(electricalEnergyRaw * Math.pow(10, ENERGY_PRECISION)) / Math.pow(10, ENERGY_PRECISION);
                        const thermalEnergy = Math.round(thermalEnergyRaw * Math.pow(10, ENERGY_PRECISION)) / Math.pow(10, ENERGY_PRECISION);

                        // Apply minimum threshold - treat very small values as zero
                        const electricalEnergyFiltered = Math.abs(electricalEnergy) < MIN_ENERGY_THRESHOLD ? 0 : Math.max(0, electricalEnergy);
                        const thermalEnergyFiltered = Math.abs(thermalEnergy) < MIN_ENERGY_THRESHOLD ? 0 : Math.max(0, thermalEnergy);

                        // Calculate COP (thermal output / electrical input)
                        const cop = electricalEnergyFiltered > 0 ? thermalEnergyFiltered / electricalEnergyFiltered : null;

                        console.log(`🔋 Energy Calculation for ${period.label}:`, {
                            electrical: {
                                start: electricalStart,
                                end: electricalEnd,
                                energyRaw: electricalEnergyRaw,
                                energyRounded: electricalEnergy,
                                energyFiltered: electricalEnergyFiltered,
                                unit: 'kWh'
                            },
                            thermal: {
                                start: thermalStart,
                                end: thermalEnd,
                                energyRaw: thermalEnergyRaw,
                                energyRounded: thermalEnergy,
                                energyFiltered: thermalEnergyFiltered,
                                unit: 'kWh'
                            },
                            precision: {
                                floatingPointError: Math.abs(electricalEnergyRaw) < MIN_ENERGY_THRESHOLD || Math.abs(thermalEnergyRaw) < MIN_ENERGY_THRESHOLD,
                                electricalDiff: electricalEnd - electricalStart,
                                thermalDiff: thermalEnd - thermalStart,
                                threshold: MIN_ENERGY_THRESHOLD
                            },
                            cop: {
                                value: cop,
                                calculation: `${thermalEnergyFiltered} / ${electricalEnergyFiltered} = ${cop}`,
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
                            electricalEnergy: electricalEnergyFiltered,
                            thermalEnergy: thermalEnergyFiltered,
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