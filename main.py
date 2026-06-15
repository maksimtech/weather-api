# main.py
from fastapi import FastAPI, HTTPException, Query
import httpx

from config import GEOCODING_URL, WEATHER_URL, REQUIRED_METRICS, WMO_CODES
from schemas import WeatherResponse, HealthResponse

app = FastAPI(
    title="Weather API", 
    description="Current weather by city using Open-Meteo with async architecture"
)


async def geocode_city(city: str, client: httpx.AsyncClient) -> dict:
    """Resolve city name to coordinates using Open-Meteo geocoding."""
    try:
        response = await client.get(
            GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Geocoding service timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {e.response.status_code}")

    data = response.json()
    results = data.get("results")
    if not results:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")

    location = results[0]
    return {
        "name": location.get("name"),
        "country": location.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }


async def fetch_weather(latitude: float, longitude: float, client: httpx.AsyncClient) -> dict:
    """Fetch current weather from Open-Meteo."""
    try:
        response = await client.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": ",".join(REQUIRED_METRICS),
                "wind_speed_unit": "kmh",
                "timezone": "auto",
            },
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Weather service timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Weather service error: {e.response.status_code}")

    return response.json()


@app.get(
    "/weather", 
    response_model=WeatherResponse,
    summary="Get current weather by city name"
)
async def get_weather(city: str = Query(..., description="City name to get weather for")):
    """
    Resolves the city name into coordinates and fetches the current weather data:
    - **temperature_c**: Temperature in Celsius
    - **humidity_percent**: Relative humidity %
    - **wind_speed_kmh**: Wind speed in km/h
    - **description**: Human-readable weather status derived from WMO code
    """
    async with httpx.AsyncClient() as client:
        location = await geocode_city(city, client)
        weather_data = await fetch_weather(location["latitude"], location["longitude"], client)

    current = weather_data.get("current")
    # Controllo di robustezza: se l'API di upstream risponde con un 200 ma omette le metriche correnti
    if not current:
        raise HTTPException(status_code=502, detail="Weather service returned a response missing 'current' conditions")

    weather_code = current.get("weather_code")

    return {
        "city": location["name"],
        "country": location.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": weather_code,
        "description": WMO_CODES.get(weather_code, "Unknown"),
        "time": current.get("time"),
    }


@app.get(
    "/health", 
    response_model=HealthResponse,
    summary="Check API health status"
)
async def health():
    """Returns the current status of the API for monitoring purposes."""
    return {"status": "ok"}