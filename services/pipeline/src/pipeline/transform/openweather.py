from pipeline.transform.openweather_normalization import (
    normalize_aqi,
    normalize_number,
    normalize_timestamp,
)

def _build_location_label(location):
  parts = [
    location["city"],
    location["country_code"],
    location.get("state"),
  ]

  return ", ".join(part for part in parts if part)


def _validate_coordinates(raw_response):
  coord = raw_response.get("coord")

  if not isinstance(coord, dict):
    raise ValueError("Missing or invalid coord object")

  lat = coord.get("lat")
  lon = coord.get("lon")

  if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
    raise ValueError("Latitude and longitude must be numeric")

  if not -90 <= lat <= 90:
    raise ValueError("Latitude is out of range")

  if not -180 <= lon <= 180:
    raise ValueError("Longitude is out of range")

  return lat, lon


def transform_air_pollution(raw_response, location):
  observations = raw_response.get("list", [])

  if not observations:
    return []

  latitude, longitude = _validate_coordinates(raw_response)
  location_label = _build_location_label(location)

  records = []

  for item in observations:
    observed_at = normalize_timestamp(item.get("dt"))
    aqi = normalize_aqi(
      item.get("main", {}).get("aqi")
    )

    # Required fields:
    # invalid timestamp or AQI means this observation
    # cannot become a clean record.
    if observed_at is None or aqi is None:
      continue

    components = item.get("components", {})

    record = {
      "location": location_label,
      "latitude": latitude,
      "longitude": longitude,
      "observed_at": observed_at,
      "aqi": aqi,
      "pm2_5": normalize_number(components.get("pm2_5")),
      "pm10": normalize_number(components.get("pm10")),
      "no2": normalize_number(components.get("no2")),
      "o3": normalize_number(components.get("o3")),
    }

    records.append(record)

  return records