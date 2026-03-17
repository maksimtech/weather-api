# Weather API

A lightweight REST API built with **FastAPI** that returns current weather data for any city, powered by the free [Open-Meteo](https://open-meteo.com/) API. No API key required.

## Features

- City name lookup via Open-Meteo geocoding
- Current temperature (°C), humidity (%), wind speed (km/h), and weather description
- Async HTTP calls with proper timeout and error handling
- Auto-generated interactive docs at `/docs`

## Requirements

- Python 3.10+

## Setup

```bash
# Clone / navigate to the project folder
cd weather-api

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Endpoints

### `GET /weather?city={city}`

Returns current weather for the specified city.

**Query parameters**

| Parameter | Type   | Required | Description      |
|-----------|--------|----------|------------------|
| `city`    | string | Yes      | City name        |

**Example request**

```
GET /weather?city=Rome
```

**Example response**

```json
{
  "city": "Rome",
  "country": "Italy",
  "latitude": 41.89474,
  "longitude": 12.48208,
  "temperature_c": 18.5,
  "humidity_percent": 62,
  "wind_speed_kmh": 14.2,
  "weather_code": 2,
  "description": "Partly cloudy",
  "time": "2026-03-17T14:00"
}
```

**Error responses**

| Status | Meaning                          |
|--------|----------------------------------|
| 404    | City not found                   |
| 502    | Upstream API returned an error   |
| 504    | Upstream API timed out           |

### `GET /health`

Returns `{"status": "ok"}`. Useful for liveness checks.

## Interactive Docs

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
