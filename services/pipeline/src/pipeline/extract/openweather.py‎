import requests

GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

def geocode_location(location, api_key):
  query = f"{location['city']}, {location.get('state', '')}, {location['country_code']}"

  params = {
    "q": query,
    "limit": 5,
    "appid": api_key,
  }

  response = requests.get(
    GEOCODING_URL,
    params=params,
    timeout=30,
  )

  response.raise_for_status()
  return response.json()