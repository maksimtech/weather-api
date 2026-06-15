# schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class WeatherResponse(BaseModel):
    city: str = Field(..., description="Name of the resolved city")
    country: Optional[str] = Field(None, description="Country of the city")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    temperature_c: Optional[float] = Field(None, description="Current temperature in Celsius")
    humidity_percent: Optional[int] = Field(None, description="Relative humidity percentage")
    wind_speed_kmh: Optional[float] = Field(None, description="Wind speed in km/h")
    weather_code: Optional[int] = Field(None, description="Raw WMO weather code")
    description: str = Field(..., description="Human-readable weather condition")
    time: Optional[str] = Field(None, description="Time of the weather reading")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Application health status")