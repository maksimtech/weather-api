# benchmarks/payloads.py
"""Static Open-Meteo style payloads used by the benchmarks.

Keeping the fixtures here makes the benchmarks fully offline and deterministic:
no upstream call is ever made, so the measurements only cover our own code.
"""


def _geocoding_result(index: int, name: str, country: str, country_code: str) -> dict:
    return {
        "id": 3169070 + index,
        "name": name,
        "latitude": 41.89474 + index / 100,
        "longitude": 12.48208 + index / 100,
        "elevation": 20.0 + index,
        "feature_code": "PPLC",
        "country_code": country_code,
        "country": country,
        "country_id": 3175395,
        "admin1": "Lazio",
        "admin2": "Roma",
        "admin3": "Roma",
        "timezone": "Europe/Rome",
        "population": 2318895 - index,
        "postcodes": ["00100", "00118", "00119"],
    }


# 10 results, as requested by geocode_city: the Italian match is the last one so
# the selection loop is fully exercised.
GEOCODING_PAYLOAD_IT_LAST = {
    "results": [
        _geocoding_result(i, "Rome", "United States", "US") for i in range(9)
    ]
    + [_geocoding_result(9, "Rome", "Italy", "IT")],
    "generationtime_ms": 0.7,
}

# No Italian match at all: geocode_city falls back to the first result.
GEOCODING_PAYLOAD_NO_IT = {
    "results": [
        _geocoding_result(i, "Paris", "France" if i == 0 else "United States",
                          "FR" if i == 0 else "US")
        for i in range(10)
    ],
    "generationtime_ms": 0.7,
}

WEATHER_PAYLOAD = {
    "latitude": 41.875,
    "longitude": 12.5,
    "generationtime_ms": 0.09,
    "utc_offset_seconds": 3600,
    "timezone": "Europe/Rome",
    "timezone_abbreviation": "CET",
    "elevation": 21.0,
    "current_units": {
        "time": "iso8601",
        "interval": "seconds",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "wind_speed_10m": "km/h",
        "weather_code": "wmo code",
    },
    "current": {
        "time": "2026-03-17T14:00",
        "interval": 900,
        "temperature_2m": 18.5,
        "relative_humidity_2m": 62,
        "wind_speed_10m": 14.2,
        "weather_code": 2,
    },
}

# Response payloads validated by the WeatherResponse pydantic model.
WEATHER_RESPONSE_PAYLOADS = [
    {
        "city": "Rome",
        "country": "Italy",
        "latitude": 41.89474,
        "longitude": 12.48208,
        "temperature_c": 18.5 + code / 10,
        "humidity_percent": 62,
        "wind_speed_kmh": 14.2,
        "weather_code": code,
        "description": "Partly cloudy",
        "time": "2026-03-17T14:00",
    }
    for code in (0, 1, 2, 3, 45, 51, 61, 71, 80, 95, 99)
]
