# GitHub Discussion: Extending Time Series Analytics Features for SensorAPI

## Discussion Title

💡 Feature Discussion: Advanced Time Series Analytics with TimescaleDB - Expanding Sensor Data Analysis Capabilities

## Discussion Category

Ideas (Feature Requests & Brainstorming)

## Discussion Content

---

### 🎯 **Overview**

Our SensorAPI currently provides basic sensor data management with PostgreSQL. As we've planned the migration to TimescaleDB (see our [TimescaleDB Migration PRD](docs/TimescaleDB_Migration_PRD.md)), we have the opportunity to implement advanced time series analytics that could dramatically enhance our sensor data analysis capabilities.

Based on [TimescaleDB's advanced analytical queries](https://docs.tigerdata.com/use-timescale/latest/query-data/advanced-analytic-queries/), I'd like to propose several analytics features that could be valuable for IoT/sensor monitoring use cases.

---

### 🔍 **Current State**

**Existing Capabilities:**

- ✅ Basic sensor readings storage with timestamps
- ✅ Latest reading tracking per sensor  
- ✅ Simple GraphQL queries for sensor data
- ✅ Time-range filtering with `startTime`/`endTime`
- ✅ Basic aggregation in GraphQL resolvers

**Current Data Model:**

```sql
-- Core time-series table (target for TimescaleDB hypertable)
api_sensor_readings (
  id UUID PRIMARY KEY,
  sensor_id UUID REFERENCES api_sensors(id),
  value DECIMAL,
  timestamp TIMESTAMPTZ,
  quality VARCHAR(20),
  raw_value DECIMAL,
  confidence_score DECIMAL
)
```

---

### 🚀 **Proposed Advanced Analytics Features**

Based on TimescaleDB's capabilities, here are the analytics features we could implement:

#### 1. **Statistical Analytics**

- **Percentile Analysis**: Calculate median, 95th percentile for sensor readings
- **Moving Averages**: Smoothed sensor data for trend analysis
- **Histogram Generation**: Distribution analysis for sensor values
- **Rate of Change**: Detect rapid changes in sensor readings

#### 2. **Time Bucket Aggregations**

- **Flexible Time Buckets**: 5-min, hourly, daily, weekly aggregations
- **Gap Filling**: Handle missing sensor data with interpolation
- **Last Observation Carried Forward (LOCF)**: Fill gaps intelligently

#### 3. **Advanced Pattern Detection**

- **Counter Reset Handling**: For sensors with monotonic counters
- **Delta Calculations**: Only return changed values to minimize data transfer
- **Anomaly Detection**: Identify unusual sensor readings
- **Cross-Sensor Correlations**: Compare metrics across sensor groups

#### 4. **Performance Optimizations**

- **Continuous Aggregates**: Pre-computed rollups for common queries
- **Last Point Queries**: Efficient "latest reading per sensor" queries
- **SkipScan Optimizations**: Faster DISTINCT queries

---

### 💡 **Implementation Ideas**

#### **Phase 1: Core Analytics GraphQL Schema**

```graphql
type SensorAnalytics {
  sensorId: ID!
  
  # Statistical functions
  percentile(percent: Float!): Float
  movingAverage(windowSize: Int!): [TimeSeriesPoint!]!
  histogram(buckets: Int!, min: Float, max: Float): HistogramData!
  
  # Time bucket aggregations  
  timeBuckets(
    interval: String!,     # "5 minutes", "1 hour", "1 day"
    aggregation: AggregationType!,  # AVG, SUM, MIN, MAX, COUNT
    fillGaps: Boolean = false
  ): [TimeBucketData!]!
  
  # Advanced patterns
  rateOfChange(timeWindow: String!): [TimeSeriesPoint!]!
  deltaChanges: [TimeSeriesPoint!]!
  anomalies(threshold: Float!): [AnomalyPoint!]!
}

type TimeBucketData {
  bucket: DateTime!
  value: Float
  count: Int!
}

type HistogramData {
  buckets: [HistogramBucket!]!
  totalCount: Int!
}

type AnomalyPoint {
  timestamp: DateTime!
  value: Float!
  expectedValue: Float!
  deviationScore: Float!
}
```

#### **Phase 2: GraphQL Resolvers Implementation**

```python
# app/graphql/resolvers/analytics.py

@strawberry.field
def sensor_analytics(sensor_id: strawberry.ID) -> SensorAnalytics:
    return SensorAnalytics(sensor_id=sensor_id)

class SensorAnalytics:
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
    
    @strawberry.field
    def percentile(self, percent: float) -> Optional[float]:
        # SELECT percentile_cont($percent) WITHIN GROUP (ORDER BY value)
        # FROM api_sensor_readings WHERE sensor_id = $sensor_id
        pass
    
    @strawberry.field  
    def moving_average(self, window_size: int) -> List[TimeSeriesPoint]:
        # SELECT timestamp, 
        #        AVG(value) OVER(ORDER BY timestamp 
        #                       ROWS BETWEEN $window_size-1 PRECEDING 
        #                       AND CURRENT ROW) AS avg_value
        # FROM api_sensor_readings WHERE sensor_id = $sensor_id
        pass
        
    @strawberry.field
    def time_buckets(self, interval: str, aggregation: AggregationType, 
                    fill_gaps: bool = False) -> List[TimeBucketData]:
        if fill_gaps:
            # time_bucket_gapfill() with LOCF
            query = """
            SELECT time_bucket_gapfill($interval, timestamp) AS bucket,
                   locf(avg(value)) AS value,
                   count(*) AS count
            FROM api_sensor_readings 
            WHERE sensor_id = $sensor_id
            GROUP BY bucket ORDER BY bucket
            """
        else:
            # Standard time_bucket()
            query = """
            SELECT time_bucket($interval, timestamp) AS bucket,
                   {}(value) AS value,
                   count(*) AS count  
            FROM api_sensor_readings
            WHERE sensor_id = $sensor_id
            GROUP BY bucket ORDER BY bucket
            """.format(aggregation.value.lower())
        pass
```

#### **Phase 3: Database Schema Optimizations**

```sql
-- Convert to TimescaleDB hypertable
SELECT create_hypertable('api_sensor_readings', 'timestamp');

-- Add indexes optimized for analytics
CREATE INDEX idx_sensor_readings_sensor_time ON api_sensor_readings (sensor_id, timestamp DESC);
CREATE INDEX idx_sensor_readings_value ON api_sensor_readings (value) WHERE value IS NOT NULL;

-- Create continuous aggregates for common queries
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT sensor_id,
       time_bucket('1 hour', timestamp) AS bucket,
       AVG(value) AS avg_value,
       MIN(value) AS min_value,
       MAX(value) AS max_value,  
       COUNT(*) AS count
FROM api_sensor_readings
GROUP BY sensor_id, bucket;
```

---

### 🎮 **Real-World Use Cases**

#### **1. Heat Pump Efficiency Analysis** (matches our [Heat Pump PRD](docs/HeatPump_Page_PRD.md))

```graphql
query HeatPumpAnalytics {
  # Electrical energy sensor
  electricalSensor: sensorAnalytics(sensorId: "electrical-meter-01") {
    timeBuckets(interval: "1 hour", aggregation: SUM, fillGaps: true) {
      bucket
      value  # kWh consumed
    }
    movingAverage(windowSize: 24) { # 24-hour rolling average
      timestamp
      value
    }
  }
  
  # Thermal energy sensor  
  thermalSensor: sensorAnalytics(sensorId: "thermal-meter-01") {
    timeBuckets(interval: "1 hour", aggregation: SUM, fillGaps: true) {
      bucket  
      value  # kWh thermal output
    }
  }
}
```

#### **2. Sensor Health Monitoring**

```graphql
query SensorHealthDashboard {
  temperatureSensor: sensorAnalytics(sensorId: "temp-01") {
    histogram(buckets: 10, min: -10.0, max: 50.0) {
      buckets {
        range
        count
      }
    }
    anomalies(threshold: 2.0) {  # 2 standard deviations
      timestamp
      value
      expectedValue
      deviationScore
    }
    deltaChanges {  # Only significant changes
      timestamp
      value
    }
  }
}
```

#### **3. Energy Production Analysis**

```graphql
query SolarPanelAnalytics {
  solarPanel: sensorAnalytics(sensorId: "solar-01") {
    rateOfChange(timeWindow: "1 hour") {
      timestamp
      value  # Rate of energy generation change
    }
    percentile(percent: 0.95)  # 95th percentile production
    timeBuckets(interval: "1 day", aggregation: SUM) {
      bucket
      value  # Daily energy production
    }
  }
}
```

---

### 🛠 **Technical Implementation Strategy**

#### **Phase 1: Foundation (2 weeks)**

1. Complete TimescaleDB migration
2. Set up hypertables and basic indexes
3. Implement core GraphQL schema for analytics

#### **Phase 2: Core Analytics (3 weeks)**  

1. Statistical functions (percentile, moving average, histogram)
2. Time bucket aggregations with gap filling
3. Basic anomaly detection

#### **Phase 3: Advanced Features (3 weeks)**

1. Continuous aggregates for performance
2. Cross-sensor correlation analysis  
3. Advanced pattern detection (rate of change, deltas)

#### **Phase 4: Optimization (2 weeks)**

1. Query performance tuning
2. Continuous aggregate refresh policies
3. Data retention policies

---

### ❓ **Discussion Questions**

1. **Priority Features**: Which analytics features would be most valuable for our IoT/sensor use cases?

2. **Performance Considerations**: How should we balance real-time analytics vs. pre-computed aggregates?

3. **API Design**: Should analytics be separate GraphQL types or integrated into existing sensor queries?

4. **Data Retention**: How long should we keep raw sensor data vs. aggregated data?

5. **Alerting Integration**: Should anomaly detection trigger alerts automatically?

6. **Multi-Tenant Support**: How should analytics work across different customers/locations?

---

### 📊 **Expected Benefits**

- **📈 Enhanced Insights**: Rich analytics capabilities for sensor data
- **⚡ Better Performance**: TimescaleDB optimizations for time-series queries  
- **🔍 Anomaly Detection**: Automatic identification of sensor issues
- **📋 Operational Dashboards**: Better visualization capabilities for frontend
- **🏭 Industrial IoT**: Advanced analytics for manufacturing/facility management
- **🌱 Energy Management**: Sophisticated analysis for renewable energy monitoring

---

### 🚧 **Potential Challenges & Solutions**

| Challenge | Proposed Solution |
|-----------|------------------|
| **Query Complexity** | Start with common use cases, build incrementally |
| **Performance Impact** | Use continuous aggregates for expensive queries |  
| **Data Volume** | Implement proper data retention and compression |
| **API Complexity** | Provide both simple and advanced analytics endpoints |
| **Migration Risk** | Implement alongside existing API, gradual rollout |

---

### 📚 **References**

- [TimescaleDB Advanced Analytical Queries](https://docs.tigerdata.com/use-timescale/latest/query-data/advanced-analytic-queries/)
- [Our TimescaleDB Migration PRD](docs/TimescaleDB_Migration_PRD.md)
- [Heat Pump Page PRD](docs/HeatPump_Page_PRD.md)
- [Current SensorAPI Architecture](PROJECT_OVERVIEW.md)

---

**What are your thoughts on these analytics features? Which ones should we prioritize? Any other time-series analytics capabilities that would be valuable for sensor data management?**

**Tags:** `enhancement`, `timescaledb`, `analytics`, `time-series`, `graphql`, `performance`
