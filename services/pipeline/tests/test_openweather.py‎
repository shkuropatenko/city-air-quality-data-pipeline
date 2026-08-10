from unittest.mock import patch

from pipeline.extract.openweather import geocode_location


def test_geocode_location_returns_coordinates(monkeypatch):
  location = {
    "city": "Charlotte",
    "country_code": "US",
    "state": "NC",
  }

  fake_response = [
    {
      "lat": 35.2271,
      "lon": -80.8431,
      "name": "Charlotte",
      "country": "US",
      "state": "North Carolina",
    }
  ]

  monkeypatch.setenv(
    "OPENWEATHER_API_KEY",
    "test-key",
  )

  with patch(
    "pipeline.extract.openweather._get_json",
    return_value=fake_response,
  ):
    result = geocode_location(location)

  assert result == {
    "lat": 35.2271,
    "lon": -80.8431,
  }