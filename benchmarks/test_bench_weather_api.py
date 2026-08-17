# benchmarks/test_bench_weather_api.py
"""CodSpeed benchmarks for the Weather API.

Every upstream HTTP call is served by an in-process ``httpx.MockTransport``, so
the benchmarks measure only our own code: request routing, the geocoding result
selection, the payload mapping and the pydantic validation/serialization.
"""

import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

import main
from config import WMO_CODES
from main import app, fetch_weather, geocode_city
from payloads import (
    GEOCODING_PAYLOAD_IT_LAST,
    GEOCODING_PAYLOAD_NO_IT,
    WEATHER_PAYLOAD,
    WEATHER_RESPONSE_PAYLOADS,
)
from schemas import WeatherResponse


def _make_handler(geocoding_payload: dict):
    """Build a MockTransport handler answering both Open-Meteo endpoints."""

    geocoding_body = json.dumps(geocoding_payload).encode()
    weather_body = json.dumps(WEATHER_PAYLOAD).encode()
    headers = {"content-type": "application/json"}

    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding" in request.url.host:
            return httpx.Response(200, content=geocoding_body, headers=headers)
        return httpx.Response(200, content=weather_body, headers=headers)

    return handler


@pytest.fixture
def loop():
    event_loop = asyncio.new_event_loop()
    yield event_loop
    event_loop.close()


@pytest.fixture
def mocked_client(loop):
    """An httpx.AsyncClient talking to the mocked upstream APIs."""
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(_make_handler(GEOCODING_PAYLOAD_IT_LAST))
    )
    yield client
    loop.run_until_complete(client.aclose())


@pytest.fixture
def test_client(monkeypatch):
    """A FastAPI TestClient whose outgoing httpx calls are mocked."""
    handler = _make_handler(GEOCODING_PAYLOAD_IT_LAST)
    real_async_client = httpx.AsyncClient

    class MockedAsyncClient(real_async_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(main.httpx, "AsyncClient", MockedAsyncClient)
    with TestClient(app) as client:
        yield client


# --------------------------------------------------------------------------- #
# Endpoint level benchmarks
# --------------------------------------------------------------------------- #


@pytest.mark.benchmark
def test_bench_weather_endpoint(test_client):
    """Full /weather round trip: routing, geocoding, mapping and validation."""
    response = test_client.get("/weather", params={"city": "Rome"})
    assert response.status_code == 200
    assert response.json()["description"] == "Partly cloudy"


@pytest.mark.benchmark
def test_bench_health_endpoint(test_client):
    """Baseline for the framework overhead on a trivial endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200


@pytest.mark.benchmark
def test_bench_openapi_schema():
    """OpenAPI generation, hit on every /docs request when the cache is cold."""
    app.openapi_schema = None
    schema = app.openapi()
    assert "/weather" in schema["paths"]


# --------------------------------------------------------------------------- #
# Coroutine level benchmarks
# --------------------------------------------------------------------------- #


def test_bench_geocode_city_italian_match(benchmark, loop, mocked_client):
    """Selection loop over 10 results where the Italian one comes last."""
    location = benchmark(
        lambda: loop.run_until_complete(geocode_city("Rome", mocked_client))
    )
    assert location["country"] == "Italy"


def test_bench_geocode_city_fallback(benchmark, loop):
    """Fallback path: no Italian result, the first one is used."""
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(_make_handler(GEOCODING_PAYLOAD_NO_IT))
    )
    try:
        location = benchmark(
            lambda: loop.run_until_complete(geocode_city("Paris", client))
        )
        assert location["country"] == "France"
    finally:
        loop.run_until_complete(client.aclose())


def test_bench_fetch_weather(benchmark, loop, mocked_client):
    """Weather fetch: query building and JSON decoding of the payload."""
    data = benchmark(
        lambda: loop.run_until_complete(
            fetch_weather(41.89474, 12.48208, mocked_client)
        )
    )
    assert data["current"]["temperature_2m"] == 18.5


# --------------------------------------------------------------------------- #
# Pure CPU benchmarks
# --------------------------------------------------------------------------- #


@pytest.mark.benchmark
def test_bench_weather_response_validation():
    """Pydantic validation of the response model for every WMO family."""
    for payload in WEATHER_RESPONSE_PAYLOADS:
        WeatherResponse.model_validate(payload)


WEATHER_RESPONSE_MODELS = [
    WeatherResponse.model_validate(payload) for payload in WEATHER_RESPONSE_PAYLOADS
]


@pytest.mark.benchmark
def test_bench_weather_response_serialization():
    """JSON serialization of the response model."""
    for model in WEATHER_RESPONSE_MODELS:
        model.model_dump_json()


@pytest.mark.benchmark
def test_bench_wmo_code_lookup():
    """Description mapping for the whole WMO code table, plus unknown codes."""
    total = 0
    for code in list(WMO_CODES) + [4, 7, 100, 255]:
        total += len(WMO_CODES.get(code, "Unknown"))
    assert total > 0
