# Heat Pump Page - Product Requirements Document

## Executive Summary

The Heat Pump Page is a focused dashboard designed to monitor heat pump energy performance and efficiency. The page provides users with clear visualization of energy consumption, production, and Coefficient of Performance (COP) calculations with flexible sensor selection and time aggregation options.

## Document Information

- **Version**: 2.0
- **Date**: September 3, 2025
- **Author**: Development Team
- **Status**: Updated after UX discussion
- **Branch**: feat-heatpumppage

## 1. Overview

### 1.1 Purpose

Create a dedicated heat pump performance dashboard that enables users to:

- Monitor energy consumption (electrical input) and production (thermal output)
- Calculate and visualize Coefficient of Performance (COP)
- Select appropriate sensors for electrical and thermal energy measurement
- View data with flexible time aggregation (hourly, daily, monthly)
- Understand heat pump efficiency patterns over time

## 2. Business Objectives

## 2. Objectives

### 2.1 Goals

- Provide clear visualization of heat pump energy performance
- Enable easy comparison between electrical input and thermal output
- Calculate and display real-time Coefficient of Performance (COP)
- Allow flexible sensor selection for different heat pump configurations
- Support time-based analysis with aggregation controls

### 2.2 Success Metrics

- Users can successfully select appropriate energy sensors within 30 seconds
- COP calculations display accurately within 5% of actual measurements
- Page load time under 3 seconds for standard time ranges
- 90% user satisfaction with chart clarity and usability

## 3. Core Features

### 3.1 Sensor Selection Interface

#### 3.1.1 Electrical Energy Selector

- **Purpose**: Select sensor measuring electrical energy consumption (heat pump input)
- **Constraint**: Only sensors with unit "kWh" are available for selection
- **UI Component**: Dropdown/select component with sensor names and descriptions
- **Data Source**: Filtered sensor list from existing sensor management system

#### 3.1.2 Thermal Energy Selector

- **Purpose**: Select sensor measuring thermal energy production (heat pump output)
- **Constraint**: Only sensors with unit "kWh" are available for selection
- **UI Component**: Dropdown/select component with sensor names and descriptions
- **Data Source**: Filtered sensor list from existing sensor management system

#### 3.1.3 Selector Synchronization

- **Behavior**: Both selectors remain synchronized for time range and aggregation settings
- **Implementation**: Shared state management for time controls
- **User Experience**: Changes to time settings apply to both charts simultaneously

### 3.2 Energy Consumption & Production Visualization

#### 3.2.1 Combined Energy Chart

- **Purpose**: Display both electrical consumption and thermal production on a single chart
- **Chart Type**: Bar chart with grouped bars for comparison
- **Data Series**:
  - Electrical Energy (kWh) - Heat pump input power consumption
  - Thermal Energy (kWh) - Heat pump output energy production
- **Time Aggregation**: Hourly, Daily, Monthly selectable options
- **Chart Library**: Chart.js for consistent styling with existing dashboard

#### 3.2.2 Coefficient of Performance (COP) Chart

- **Purpose**: Display calculated COP values separately for clear efficiency analysis
- **Chart Type**: Bar chart showing COP values over time
- **Calculation**: COP = Thermal Energy Output / Electrical Energy Input
- **Data Processing**: COP calculated from selected sensor data in real-time
- **Visual Indicators**: Efficiency thresholds and target performance bands

#### 3.2.3 Time Controls

- **Time Range Selector**: Last 24 hours, Last 7 days, Last 30 days, Custom range
- **Aggregation Controls**: Hourly, Daily, Monthly data grouping
- **Synchronization**: Time settings apply to both energy and COP charts
- **Real-time Updates**: Manual refresh by reloading the page (no auto-refresh)

### 3.3 User Experience Specifications

#### 3.3.1 Sensor Selection Workflow

1. User opens heat pump page
2. Two sensor selectors displayed prominently at top of page
3. Each selector shows only sensors with "kWh" unit
4. Default selection shows "Please select a sensor" placeholder
5. Both selectors must have selections before charts display data

#### 3.3.2 Data Loading & Error Handling

- **Loading States**: Skeleton loaders for charts during data fetch
- **Error Handling**: Clear error messages for sensor connectivity issues
- **No Data States**: Friendly messages when sensors have no data for selected time range
- **Sensor Validation**: Warning if selected sensors don't have recent data
- **Component Health Monitoring**: Compressor, fans, coils status
- **Maintenance Predictions**: When components may need service
- **Performance Degradation Alerts**: Early warning signs
- **Service Scheduling Integration**: Connect with local HVAC providers


## 4. Technical Requirements

### 4.1 Frontend Implementation

#### 4.1.1 Technology Stack

- **Framework**: React with TypeScript (existing architecture)
- **Chart Library**: Chart.js for consistent visualization
- **State Management**: React Context or Redux for sensor selections and time controls
- **Styling**: CSS modules or styled-components matching existing design system

#### 4.1.2 Component Architecture

```
/src/pages/HeatPump/
├── index.tsx                 # Main heat pump page component
├── components/
│   ├── SensorSelector.tsx    # Reusable sensor selection component
│   ├── EnergyChart.tsx       # Combined energy consumption/production chart
│   ├── COPChart.tsx          # Coefficient of Performance chart
│   └── TimeControls.tsx     # Time range and aggregation controls
├── hooks/
│   ├── useSensorData.tsx     # Custom hook for sensor data fetching
│   └── useCOPCalculation.tsx # Custom hook for COP calculations
└── types/
    └── heatpump.types.ts     # TypeScript interfaces and types
```

### 4.2 Backend Integration

#### 4.2.1 Data Requirements

- **Sensor Filtering**: API endpoint to retrieve sensors filtered by unit "kWh"
- **Time-Series Data**: Aggregate sensor readings by hour/day/month
- **Real-time Calculations**: COP computation from selected sensor pairs
- **Data Validation**: Ensure sensor data quality and availability

#### 4.2.2 API Endpoints

```typescript
// Sensor filtering by sensortype unit
GET /api/sensors?filter[sensortype.unit]=kWh    # Filtered sensor list
GET /api/sensors/{id}/readings                  # Time-series meter readings
POST /api/heatpump/cop-calculation              # COP calculation service

// Query parameters for time-series data
interface SensorReadingsQuery {
  startTime: string;
  endTime: string;
  aggregation: 'hour' | 'day' | 'month';
}
```

### 4.3 Data Processing

#### 4.3.1 COP Calculation Logic

```typescript
interface COPCalculation {
  timestamp: string;
  electricalEnergy: number;    // kWh consumed in time period
  thermalEnergy: number;       // kWh produced in time period
  cop: number;                 // thermalEnergy / electricalEnergy
}

// Energy calculation from meter readings (cumulative values)
function calculateEnergyConsumption(
  startReading: number, 
  endReading: number
): number {
  return endReading - startReading;
}

// COP calculation with error handling
function calculateCOP(
  electricalStart: number, 
  electricalEnd: number,
  thermalStart: number, 
  thermalEnd: number
): number | null {
  const electricalEnergy = calculateEnergyConsumption(electricalStart, electricalEnd);
  const thermalEnergy = calculateEnergyConsumption(thermalStart, thermalEnd);
  
  if (electricalEnergy <= 0) return null;
  return thermalEnergy / electricalEnergy;
}
```

#### 4.3.2 Data Aggregation

- **Hourly**: Calculate energy delta between start/end of hour, average COP per hour
- **Daily**: Calculate energy delta between start/end of day, average COP per day  
- **Monthly**: Calculate energy delta between start/end of month, average COP per month
- **Meter Reading Logic**: Energy = End Reading - Start Reading for each time period
- **Sync Requirements**: Both charts use identical time buckets and calculation method

## 5. User Experience Requirements

### 5.1 Design Principles

- **Focused Functionality**: Clear energy and COP visualization without complexity
- **Intuitive Navigation**: Sensor selection and time controls prominently displayed
- **Mobile Responsive**: Optimized for desktop and tablet viewing
- **Consistency**: Match existing sensor dashboard design patterns

### 5.2 Visual Design

- **Chart Layout**: Stacked vertically with energy chart above COP chart
- **Color Scheme**: Distinct colors for electrical (blue) and thermal (orange) energy
- **Interactive Elements**: Hover tooltips, time range selectors, sensor dropdowns
- **Loading States**: Skeleton placeholders during data fetching

### 5.3 User Workflow

1. **Page Load**: Display sensor selectors and empty chart placeholders
2. **Sensor Selection**: User selects electrical and thermal energy sensors
3. **Data Display**: Charts populate with default time range (last 24 hours)
4. **Time Adjustment**: User can change time range and aggregation
5. **Data Refresh**: Manual page reload to update data

## 6. Implementation Roadmap

### 6.1 MVP Features (Phase 1)

- [ ] Sensor selection interface with kWh filtering
- [ ] Combined energy consumption/production chart
- [ ] Separate COP calculation and visualization
- [ ] Time range controls (24h, 7d, 30d)
- [ ] Data aggregation (hourly, daily, monthly)
- [ ] Basic error handling and loading states

### 6.2 Success Criteria

- **Functional**: Both sensor selectors work and filter correctly
- **Accurate**: COP calculations are mathematically correct
- **Responsive**: Charts update when time controls change
- **Reliable**: Error states handle missing or invalid data gracefully

## 7. Future Enhancements

### 7.1 Potential Improvements

- [ ] Auto-refresh capability with configurable intervals
- [ ] Data export functionality (CSV, PDF)
- [ ] Advanced time range picker (custom date ranges)
- [ ] Performance benchmarking against industry standards
- [ ] Alert thresholds for low COP values

### 7.2 Integration Opportunities

- [ ] Weather data overlay for efficiency correlation
- [ ] Cost calculation based on energy rates
- [ ] Maintenance scheduling based on runtime hours
- [ ] Mobile app companion for remote monitoring

## 8. Conclusion

This simplified heat pump monitoring page focuses on the core functionality of energy consumption, production tracking, and COP analysis. The implementation prioritizes clear data visualization and user-friendly sensor selection while building on the existing sensor infrastructure.

The design decisions ensure a focused user experience that delivers valuable heat pump performance insights without overwhelming complexity. Future enhancements can be added incrementally based on user feedback and additional requirements.

## 8. Technical Architecture

### 8.1 Frontend Components
```
/src/pages/HeatPump/
├── HeatPumpDashboard.tsx          # Main dashboard page
├── components/
│   ├── StatusOverview.tsx         # System status cards
│   ├── PerformanceCharts.tsx      # COP and efficiency charts
│   ├── EnergyConsumption.tsx      # Energy usage tracking
│   ├── TemperatureControl.tsx     # Temperature settings
│   ├── MaintenanceAlerts.tsx      # Alert notifications
│   └── HistoricalData.tsx         # Historical performance
└── hooks/
    ├── useHeatPumpData.tsx        # Real-time data fetching
    ├── usePerformanceMetrics.tsx  # Performance calculations
    └── useAlerts.tsx              # Alert management
```

### 8.2 Backend Integration
```
/app/
├── api/endpoints/heatpump.py      # Heat pump API endpoints
├── models/heatpump.py             # Data models
├── services/heatpump_service.py   # Business logic
└── graphql/
    ├── heatpump_types.py          # GraphQL types
    └── heatpump_resolvers.py      # GraphQL resolvers
```

### 8.3 Database Schema
```sql
-- Heat pump systems table
CREATE TABLE heat_pump_systems (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    model VARCHAR(100),
    installed_date DATE,
    capacity_btu INTEGER,
    efficiency_rating DECIMAL(3,1)
);

-- Real-time performance data (TimescaleDB hypertable)
CREATE TABLE heat_pump_performance (
    timestamp TIMESTAMPTZ NOT NULL,
    system_id INTEGER REFERENCES heat_pump_systems(id),
    indoor_temp DECIMAL(4,1),
    outdoor_temp DECIMAL(4,1),
    target_temp DECIMAL(4,1),
    power_consumption DECIMAL(8,2),
    cop DECIMAL(4,2),
    operating_mode VARCHAR(20),
    runtime_minutes INTEGER
);
```

## 9. Development Timeline

### Phase 1 (4 weeks) - MVP
- **Week 1**: Database schema and backend API development
- **Week 2**: Core frontend components and basic dashboard
- **Week 3**: Real-time data integration and charts
- **Week 4**: Testing, responsive design, and deployment

### Phase 2 (6 weeks) - Enhanced Features
- **Weeks 5-6**: Advanced analytics and reporting
- **Weeks 7-8**: Predictive maintenance features
- **Weeks 9-10**: Mobile app integration and optimization

## 10. Risk Assessment

### 10.1 Technical Risks
- **Data Accuracy**: Sensor calibration and data quality issues
- **Real-time Performance**: High-frequency data processing load
- **Integration Complexity**: Multiple sensor types and protocols

### 10.2 Mitigation Strategies
- **Data Validation**: Implement robust data validation and outlier detection
- **Performance Optimization**: Use efficient data structures and caching
- **Modular Design**: Build flexible integration layer for various sensors

## 11. Success Criteria

### 11.1 Launch Criteria
- [ ] All MVP features functional and tested
- [ ] Page load time under 3 seconds
- [ ] Mobile responsiveness verified
- [ ] Real-time data updates working correctly
- [ ] Basic alert system operational

### 11.2 Post-Launch Metrics
- User engagement with heat pump page
- Energy consumption reduction in monitored systems
- Alert accuracy and user response rates
- Customer satisfaction scores

---

**Document Status**: Ready for review and implementation planning
**Next Steps**: Technical specification development and UI/UX mockups