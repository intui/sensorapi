import { useMemo } from 'react';
import type { EnergyReading, COPCalculation, AggregationType } from '../types/heatpump.types';

interface UseCOPCalculationProps {
  electricalReadings: EnergyReading[];
  thermalReadings: EnergyReading[];
  aggregation: AggregationType;
}

interface UseCOPCalculationReturn {
  copData: COPCalculation[];
  isCalculating: boolean;
  error: string | null;
}

// Helper function to calculate energy consumption from meter readings
const calculateEnergyConsumption = (startReading: number, endReading: number): number => {
  return Math.max(0, endReading - startReading);
};

// Helper function to group readings by time period
const groupReadingsByPeriod = (readings: EnergyReading[], aggregation: AggregationType): Map<string, EnergyReading[]> => {
  const groups = new Map<string, EnergyReading[]>();
  
  readings.forEach(reading => {
    const date = new Date(reading.timestamp);
    let key: string;
    
    switch (aggregation) {
      case 'hour':
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
        break;
      case 'day':
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
        break;
      case 'month':
        key = `${date.getFullYear()}-${date.getMonth()}`;
        break;
      default:
        key = date.toISOString();
    }
    
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key)!.push(reading);
  });
  
  return groups;
};

// Helper function to get period label
const getPeriodLabel = (readings: EnergyReading[], aggregation: AggregationType): string => {
  if (readings.length === 0) return '';
  
  const date = new Date(readings[0].timestamp);
  
  switch (aggregation) {
    case 'hour':
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: 'numeric',
        hour12: true
      });
    case 'day':
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    case 'month':
      return date.toLocaleDateString('en-US', { 
        month: 'long',
        year: 'numeric'
      });
    default:
      return date.toISOString();
  }
};

export const useCOPCalculation = ({
  electricalReadings,
  thermalReadings,
  aggregation
}: UseCOPCalculationProps): UseCOPCalculationReturn => {
  
  const copData = useMemo((): COPCalculation[] => {
    if (electricalReadings.length === 0 || thermalReadings.length === 0) {
      return [];
    }

    try {
      // Group readings by time period
      const electricalGroups = groupReadingsByPeriod(electricalReadings, aggregation);
      const thermalGroups = groupReadingsByPeriod(thermalReadings, aggregation);
      
      const copCalculations: COPCalculation[] = [];
      
      // Calculate COP for each time period that has both electrical and thermal data
      for (const [periodKey, electricalPeriodReadings] of electricalGroups) {
        const thermalPeriodReadings = thermalGroups.get(periodKey);
        
        if (!thermalPeriodReadings || electricalPeriodReadings.length < 2 || thermalPeriodReadings.length < 2) {
          continue; // Skip periods without sufficient data
        }
        
        // Sort readings by timestamp
        const sortedElectrical = [...electricalPeriodReadings].sort((a, b) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
        const sortedThermal = [...thermalPeriodReadings].sort((a, b) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
        
        // Calculate energy consumption for the period (end reading - start reading)
        const electricalStart = sortedElectrical[0].value;
        const electricalEnd = sortedElectrical[sortedElectrical.length - 1].value;
        const thermalStart = sortedThermal[0].value;
        const thermalEnd = sortedThermal[sortedThermal.length - 1].value;
        
        const electricalEnergy = calculateEnergyConsumption(electricalStart, electricalEnd);
        const thermalEnergy = calculateEnergyConsumption(thermalStart, thermalEnd);
        
        // Calculate COP (thermal output / electrical input)
        const cop = electricalEnergy > 0 ? thermalEnergy / electricalEnergy : null;
        
        copCalculations.push({
          timestamp: getPeriodLabel(sortedElectrical, aggregation),
          electricalEnergy,
          thermalEnergy,
          cop
        });
      }
      
      // Sort by timestamp
      return copCalculations.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
      
    } catch (error) {
      console.error('Error calculating COP:', error);
      return [];
    }
  }, [electricalReadings, thermalReadings, aggregation]);

  return {
    copData,
    isCalculating: false, // Since we're doing sync calculation
    error: null
  };
};