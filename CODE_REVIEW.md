# SensorAPI – Code Review (2025-08-08)

This document summarizes architectural observations, risks, and concrete recommendations to improve maintainability, performance, and deployment reliability.

## Overview

- Stack: FastAPI + Strawberry (GraphQL), SQLAlchemy, Postgres; React + Vite + Apollo Client; Vercel deployment.
- Structure separation is good (backend `app/`, serverless entry `api/main.py`, frontend `frontend/`).

## Backend (FastAPI/Strawberry)

- CORS: Currently `allow_origins=["*"]` with `allow_credentials=True`. In production, restrict origins (your Vercel domain) and/or set `allow_credentials=False` if not using cookies.
- Auto table creation: `Base.metadata.create_all()` exists in both `main.py` and `api/main.py`. Remove in production and rely on Alembic migrations to reduce cold start and ensure schema parity.
- Duplicate schema definition: `app/graphql/schema.py` is the source of truth. Drop the extra `schema = strawberry.Schema(...)` at bottom of `app/graphql/resolvers.py`.

## Database (SQLAlchemy)

- Serverless connection strategy: Intention is NullPool, but `poolclass=None` does not enforce it. Use `from sqlalchemy.pool import NullPool` and set `poolclass=NullPool` in `create_engine`.
- Cascades:
  - ORM-level cascade exists: `Sensor.readings` has `cascade="all, delete-orphan"`.
  - Add DB-level cascades: set `ondelete="CASCADE"` on FKs (e.g., `api_sensor_readings.sensor_id` → `api_sensors.id`). Consider `passive_deletes=True` on relationships to leverage DB cascades.
  - After DB-level cascades, simplify `delete_sensor` mutation (no manual child deletes).
- SQLAlchemy modern API: Use `from sqlalchemy.orm import declarative_base` instead of `sqlalchemy.ext.declarative.declarative_base`.

## GraphQL (Schema/Resolvers)

- N+1 queries: `Sensor.sensor_type`, `Sensor.location`, and `SensorReading.sensor` trigger extra queries per row. Adopt DataLoader or appropriate eager loading.
- Consistency: `types.py` contains `@strawberry.field` methods for nested fields, while `resolvers.py` reassigns resolvers dynamically. Pick one approach (recommend: methods in `types.py`) and remove dynamic reassignment.
- Validation:
  - `create_sensor` should validate `sensor_type_id` and `location_id` existence; return clear errors.
  - Use Strawberry `Enum` for `Alert.status`/`severity` to prevent invalid values.
- Pagination/limits:
  - `sensor_readings` uses limit/offset without a max cap. Enforce a safe maximum (e.g., 1000) and consider cursor-based pagination for time-series.
- Unimplemented fields:
  - `Sensor.latest_reading` and `Alert.reading` return `None`. Implement resolvers or remove these fields.
- Minor: Remove unused imports (e.g., `and_`, `Session`) from `resolvers.py`.

## Config/Settings

- `SECRET_KEY` has a default. Fail fast if `ENVIRONMENT=production` and default is used.
- Ensure Vercel env vars are complete: `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT=production`, `DEBUG=false`.

## Frontend (Vite/React/Apollo)

- Endpoint logic: Good. Prod uses relative `/graphql`; dev uses `VITE_GRAPHQL_ENDPOINT`.
- Error UI: With `errorPolicy: 'all'`, ensure components surface `error` and partial data states clearly.
- Types/state: Guard for `undefined` data shapes in pages.

## Deployment (Vercel)

- Current `vercel.json`:
  - Builds frontend: `buildCommand: "cd frontend && npm ci && npm run build"` and `outputDirectory: "frontend/dist"`.
  - Rewrites `/graphql`, `/api/(.*)`, `/health` → `/api/main` (good).
- SPA fallback for React Router (avoid 404 on deep links):
  - Add filesystem-first rule and index fallback, e.g. in `routes` format:
    - `{ "handle": "filesystem" }`
    - `{ "src": "/(.*)", "dest": "/index.html" }`
  - If staying with `rewrites`, ensure assets resolve before catch-all and add a final rewrite to `/index.html`.
- Explicit Python runtime for functions:
  - `"functions": { "api/**/*.py": { "runtime": "python3.11" } }` to avoid runtime version errors.
- Dependencies: Ensure the runtime installs the correct requirements (unify on `requirements.txt` or configure Vercel to use `requirements-vercel.txt`).
- CORS: Since FE/BE are same origin in prod, restrict CORS to your domain.

## Testing/Quality

- Use Alembic migrations for all schema changes (ondelete cascades, new indexes) and remove `create_all` in serverless.
- Add unit tests for resolvers and integration tests for CRUD flows.
- Add CI for Python (ruff/black/mypy) and frontend (ESLint/TypeScript build).

## Performance/Observability

- Index coverage is good for time-series. Consider retention strategies and partitioning if volume grows.
- Add structured request/DB logging and basic metrics.
- Consider simple caching for heavy read queries if applicable.

## Security

- Do not commit real `.env` values. Ensure secrets live in Vercel.
- Tighten CORS in prod.
- Validate inputs server-side (IDs, numeric bounds) to avoid bad writes.

## Priority Actions (Quick Wins)

1. Switch to `NullPool` in `create_engine` for serverless reliability.
2. Add SPA fallback in `vercel.json` to fix React Router 404s.
3. Remove `create_all` from `api/main.py`; rely on Alembic migrations.
4. Remove duplicate `schema` and dynamic field resolver assignments; use a single approach.
5. Add DB-level `ondelete="CASCADE"` and `passive_deletes=True`; then simplify `delete_sensor`.
6. Restrict CORS in production.

## Suggested Follow-up 

- I can apply (1) and (2) immediately, then stage the cascade + migration work (5) in a separate PR to avoid production disruption.
