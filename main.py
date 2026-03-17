from fastapi import FastAPI, HTTPException, Query
import httpx

app = FastAPI(title="Weather API", description="Current weather by city using Open-Meteo")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather interpretation codes
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


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
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
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


@app.get("/weather")
async def get_weather(city: str = Query(..., description="City name to get weather for")):
    """
    Returns current weather for the given city:
    - **temperature**: °C
    - **description**: human-readable weather condition
    - **humidity**: relative humidity %
    - **wind_speed**: km/h
    """
    async with httpx.AsyncClient() as client:
        location = await geocode_city(city, client)
        weather_data = await fetch_weather(location["latitude"], location["longitude"], client)

    current = weather_data.get("current", {})
    weather_code = current.get("weather_code")

    return {
        "city": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": weather_code,
        "description": WMO_CODES.get(weather_code, "Unknown"),
        "time": current.get("time"),
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
