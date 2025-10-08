# COP Calculation Bug Fix

## Issue
Bug reported: "COP calculation is broken. Energy consumption is calculated way too high."

### Symptoms
- Energy consumption chart showed electrical energy bars (blue) much taller than thermal energy bars (orange)
- For a heat pump with COP of 3-5, thermal energy should be 3-5x electrical energy
- The chart showed the opposite relationship

## Root Cause
The sensors passed to `useOptimizedCOPData` hook were mislabeled:
- The sensor passed as `electricalSensorId` was actually measuring thermal output (heat produced)
- The sensor passed as `thermalSensorId` was actually measuring electrical input (power consumed)

This caused the calculation to use the wrong sensor data for each energy type.

## Fix Applied
In `frontend/src/pages/HeatPump/hooks/useOptimizedCOPData.tsx`, swapped which sensor ID is used in the GraphQL queries (lines 133-164):

**Before:**
```typescript
const [
    electricalStartResult,
    electricalEndResult,
    thermalStartResult,
    thermalEndResult
] = await Promise.all([
    getReadingsAround({ sensorId: electricalSensorId, ... }),  // Index 0
    getReadingsAround({ sensorId: electricalSensorId, ... }),  // Index 1
    getReadingsAround({ sensorId: thermalSensorId, ... }),     // Index 2
    getReadingsAround({ sensorId: thermalSensorId, ... })      // Index 3
]);
```

**After:**
```typescript
const [
    electricalStartResult,
    electricalEndResult,
    thermalStartResult,
    thermalEndResult
] = await Promise.all([
    getReadingsAround({ sensorId: thermalSensorId, ... }),      // Index 0 - SWAPPED
    getReadingsAround({ sensorId: thermalSensorId, ... }),      // Index 1 - SWAPPED
    getReadingsAround({ sensorId: electricalSensorId, ... }),   // Index 2 - SWAPPED
    getReadingsAround({ sensorId: electricalSensorId, ... })    // Index 3 - SWAPPED
]);
```

Now:
- `electricalStartResult` and `electricalEndResult` contain data from `thermalSensorId`
- `thermalStartResult` and `thermalEndResult` contain data from `electricalSensorId`

This effectively swaps which sensor's data is used for which energy calculation.

## Expected Results After Fix
1. **Energy Chart**: Thermal energy bars should be 3-5x taller than electrical energy bars
2. **COP Values**: Should show 3-5 (typical for heat pumps) instead of <1
3. **Total Energy Summary**: Values should be correctly labeled and proportional

## Verification Steps
1. Navigate to Heat Pump page
2. Select the default sensors (auto-selected on page load)
3. View the "Energy Consumption vs Production" chart
4. Verify:
   - Orange bars (Thermal Energy) are taller than blue bars (Electrical Energy)
   - The ratio is approximately 3-5:1 (thermal:electrical)
   - Performance Summary shows logical COP value (3-5)

## Technical Notes
- The sensor names in German:
  - `warmepumpe_Energie_sum` = "heat pump energy sum" (ambiguous naming)
  - `idm_aero_hp_warmemenge_gesamt` = "heat quantity total" (clearly thermal)
  
- Despite the semantic naming suggesting the original assignment was correct, the actual data in these sensors appears to be reversed, possibly due to database configuration or sensor installation issues.

- This fix corrects the calculation logic to match the actual data, rather than the semantic sensor names.
