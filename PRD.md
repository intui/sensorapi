# Product Requirements Document (PRD) - SensorAPI

## Overview

This document outlines new features and enhancements for the SensorAPI to improve real-time sensor status tracking and data management.

## Features

### 1. Automatic Sensor Status Updates

**Priority:** High  
**Status:** Not Started  
**Estimated Effort:** Medium  

#### Description
Automatically update sensor metadata when new readings are received to maintain accurate real-time status information.

#### Requirements

##### 1.1 Update Latest Reading Reference
- **Task:** Update `sensor.latestReading` after a new sensor reading occurs
- **Acceptance Criteria:**
  - When a new `SensorReading` is created, automatically update the corresponding `Sensor.latest_reading` field
  - The latest reading should always point to the most recent reading by timestamp
  - Ensure atomic updates to prevent race conditions
  - Add GraphQL field resolver for `Sensor.latestReading` to return the actual reading data

##### 1.2 Update Sensor Online Status
- **Task:** Set `sensor.isOnline` based on recent activity
- **Acceptance Criteria:**
  - Mark sensor as online (`isOnline = true`) when a new reading is received
  - Mark sensor as offline (`isOnline = false`) if no readings received within configurable threshold (default: 5 minutes)
  - Implement background job or trigger to check and update offline sensors periodically

##### 1.3 Update Last Seen Timestamp
- **Task:** Set `sensor.lastSeen` when sensor activity occurs
- **Acceptance Criteria:**
  - Update `lastSeen` timestamp whenever a new reading is received
  - Use the reading's `timestamp` field (when measurement was taken) or `received_at` (when API received it)
  - Ensure timestamp is in UTC

##### 1.4 Sensor Activation Management
- **Task:** Manage `sensor.isActive` status appropriately
- **Acceptance Criteria:**
  - New sensors should default to `isActive = true`
  - Provide GraphQL mutation to manually activate/deactivate sensors
  - Inactive sensors should still accept readings but may be filtered from default queries
  - after receiving a sensor reading the status is set to active
  - Consider auto-deactivation for sensors offline for extended periods (configurable, e.g., 24 hours)

#### Technical Implementation

##### Database Changes
- Ensure `Sensor.latest_reading_id` foreign key exists and is properly indexed
- Add database triggers or use ORM event listeners for automatic updates
- Consider adding `last_reading_at` field for faster queries without joins

##### GraphQL Schema Updates
```graphql
type Sensor {
  # Existing fields...
  latestReading: SensorReading  # Implement this resolver
  isOnline: Boolean!
  lastSeen: DateTime
  isActive: Boolean!
}

input UpdateSensorStatusInput {
  isActive: Boolean
}

type Mutation {
  updateSensorStatus(id: ID!, input: UpdateSensorStatusInput!): Sensor
}
```

##### Background Jobs
- Implement periodic job to check sensor online status
- Use APScheduler or similar for Python background tasks
- Consider Redis for job queuing in production

#### Dependencies
- Database migration to add any missing fields/indexes
- Background job scheduler setup
- Consider caching layer for frequently accessed sensor status

#### Testing Requirements
- Unit tests for status update logic
- Integration tests for GraphQL mutations
- Performance tests for bulk status updates
- Test edge cases (duplicate readings, out-of-order timestamps)

#### Monitoring & Metrics
- Track sensor online/offline status changes
- Monitor background job execution
- Alert on sensors going offline unexpectedly
- Dashboard showing sensor health overview

---

## Future Enhancements (Backlog)

### Sensor Health Scoring
- Calculate health score based on reading frequency, data quality, and uptime
- Predictive offline detection based on reading patterns

### Batch Status Updates
- Optimize database updates for high-volume scenarios
- Bulk operations for sensor status management

### Sensor Groups/Tags
- Group sensors by location, type, or custom tags
- Bulk operations on sensor groups

### Alert Rules Engine
- Configurable rules for sensor offline alerts
- Integration with notification systems (email, Slack, etc.)

---

## Notes

- Ensure backward compatibility with existing API consumers
- Consider rate limiting for sensor reading ingestion
- Plan for horizontal scaling if sensor volume grows significantly
- Document new features in GraphQL schema descriptions
