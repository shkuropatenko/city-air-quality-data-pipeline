import os
from unittest import mock
from unittest.mock import patch

import pytest

from pipeline.extract.openweather import (
  geocode_location,
  fetch_air_pollution_history,
)

@pytest.fixture(autouse=True)
def set_test_key():
  with mock.patch.dict(
    os.environ,
    {"OPENWEATHER_API_KEY": "test-key"},
  ):
    yield

def test_fetch_air_pollution_history_empty_response():

  with patch(
    "pipeline.extract.openweather._get_json",
    return_value={"list": []},
  ):
    with pytest.raises(
      ValueError,
      match="No air pollution data returned",
    ):
      fetch_air_pollution_history(
        lat=35.2271,
        lon=-80.8431,
        start=1606480000,
        end=1606485000,
      )

def test_geocode_location_returns_coordinates():
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

  with patch(
    "pipeline.extract.openweather._get_json",
    return_value=fake_response,
  ):
    result = geocode_location(location)

  assert result == {
    "lat": 35.2271,
    "lon": -80.8431,
  }

def test_geocode_location_not_found():
  location = {
    "city": "UnknownCity",
    "country_code": "US",
    "state": "",
  }

  with patch(
    "pipeline.extract.openweather._get_json",
    return_value=[],
):
    with pytest.raises(ValueError, match="Location not found"):
      geocode_location(location)




def test_fetch_air_pollution_history_returns_data():

  fake_response = {
    "coord": {
        "lon": -80.8431,
        "lat": 35.2271,
    },
    "list": [
      {
        "dt": 1606482000,
        "main": {
          "aqi": 2,
        },
        "components": {
          "pm2_5": 13.448,
          "pm10": 15.524,
          "no2": 43.184,
          "o3": 4.783,
        },
      }
    ],
  }

  with patch(
    "pipeline.extract.openweather._get_json",
    return_value=fake_response,
  ):
    result = fetch_air_pollution_history(
      lat=35.2271,
      lon=-80.8431,
      start=1606480000,
      end=1606485000,
    )

  assert result == fake_response

def test_geocode_location_without_state():
  location = {
    "city": "London",
    "country_code": "GB",
  }

  fake_response = [
    {
      "lat": 51.5074,
      "lon": -0.1278,
    }
  ]

  with patch(
    "pipeline.extract.openweather._get_json",
    return_value=fake_response,
  ) as mock_get_json:
    geocode_location(location)

  params = mock_get_json.call_args.args[1]

  assert params["q"] == "London,GB"