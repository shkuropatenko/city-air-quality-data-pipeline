import os
import requests


GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
AIR_POLLUTION_HISTORY_URL = (
  "https://api.openweathermap.org/data/2.5/air_pollution/history"
)


def get_api_key():
  api_key = os.getenv("OPENWEATHER_API_KEY")

  if not api_key:
    raise ValueError("OPENWEATHER_API_KEY is not set")

  return api_key

def _get_json(url, params):
  try:
    response = requests.get(
      url,
      params=params,
      timeout=30,
    )
    response.raise_for_status()
    return response.json()

  except requests.RequestException as exc:
    raise RuntimeError(f"OpenWeather request failed: {exc}") from exc

def geocode_location(location):
  api_key = get_api_key()

  query_parts = [location["city"]]

  if location.get("state"):
    query_parts.append(location["state"])

  query_parts.append(location["country_code"])

  query = ",".join(query_parts)

  params = {
    "q": query,
    "limit": 1,
    "appid": api_key,
  }

  data = _get_json(GEOCODING_URL, params)

  if not data:
    raise ValueError(f"Location not found: {query}")

  first_match = data[0]

  return {
    "lat": first_match["lat"],
    "lon": first_match["lon"],
  }


def fetch_air_pollution_history(lat, lon, start, end):
  api_key = get_api_key()

  if start > end:
    raise ValueError("Start time must be before or equal to end time")

  params = {
    "lat": lat,
    "lon": lon,
    "start": start,
    "end": end,
    "appid": api_key,
  }

  data = _get_json(AIR_POLLUTION_HISTORY_URL, params)

  if not data.get("list"):
    raise ValueError("No air pollution data returned")

  return data