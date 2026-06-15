Requirements

    Python 3.10+

Setup
Bash

# Clone / navigate to the project folder
cd weather-api

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

Running
Bash

uvicorn main:app --reload

The API will be available at http://localhost:8000.
Endpoints
GET /weather?city={city}

Returns current weather for the specified city.
Query parameters
Parameter	Type	Required	Description
city	string	Yes	City name to look up
Response Schema (validated via Pydantic)

    city (string): Name of the resolved city

    country (string, optional): Country of the city

    latitude (float): Latitude coordinate

    longitude (float): Longitude coordinate

    temperature_c (float): Current temperature in Celsius

    humidity_percent (integer): Relative humidity percentage

    wind_speed_kmh (float): Wind speed in km/h

    weather_code (integer): Raw WMO weather code

    description (string): Human-readable weather condition

    time (string): Time of the weather reading (ISO format)

Example request
HTTP

GET /weather?city=Rome

Example response
JSON

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

Error responses
Status	Meaning
404	City not found
502	Upstream API returned an error or malformed payload
504	Upstream API timed out
GET /health

Returns {"status": "ok"}. Useful for liveness checks and monitoring.
Interactive Docs

Once the server is running, visit:

    Swagger UI: http://localhost:8000/docs

    ReDoc: http://localhost:8000/redoc
    """

with open("weather_api_v2/config.py", "w") as f: f.write(config_content)
with open("weather_api_v2/schemas.py", "w") as f: f.write(schemas_content)
with open("weather_api_v2/main.py", "w") as f: f.write(main_content)
with open("weather_api_v2/requirements.txt", "w") as f: f.write(requirements_content)
with open("weather_api_v2/.gitignore", "w") as f: f.write(gitignore_content)
with open("weather_api_v2/README.md", "w") as f: f.write(readme_content)

print("Files successfully generated.")