# City Air Quality Data Pipeline

A data engineering project that collects historical air-quality data for multiple cities using the OpenWeather API and prepares it for storage, analysis, and visualization.

The project is being built as an end-to-end data pipeline: city configuration → geocoding → air-quality extraction → transformation → PostgreSQL → API → dashboard.

## Project Goals

- Read and validate configured city locations
- Resolve cities to geographic coordinates
- Extract historical air-quality data from OpenWeather
- Preserve raw API responses before transformation
- Transform pollution measurements into structured datasets
- Store processed data in PostgreSQL
- Expose the data through an API
- Visualize air-quality trends in a dashboard

## Architecture

```text
City Configuration
        ↓
OpenWeather Geocoding API
        ↓
Latitude / Longitude
        ↓
OpenWeather Air Pollution API
        ↓
Raw API Data
        ↓
Data Transformation
        ↓
PostgreSQL
        ↓
Python API
        ↓
React Dashboard
```
