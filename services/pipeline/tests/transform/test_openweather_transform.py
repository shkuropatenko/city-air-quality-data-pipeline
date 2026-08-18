from datetime import datetime, timezone

import pytest

from pipeline.transform.openweather import transform_air_pollution


def test_transform_returns_clean_record():
  raw_response = {
    "coord": {
      "lat": 50,
      "lon": 50,
    },
    "list": [
      {
        "dt": 1606489200,
        "main": {
          "aqi": 1,
        },
        "components": {
          "pm2_5": 0.9,
          "pm10": 0.93,
          "no2": 2.29,
          "o3": 46.49,
        },
      }
    ],
  }

  location = {
    "city": "Raleigh",
    "country_code": "US",
    "state": "NC",
  }

  result = transform_air_pollution(raw_response, location)

  assert result == [
    {
      "location": "Raleigh, US, NC",
      "latitude": 50,
      "longitude": 50,
      "observed_at": datetime(
        2020,
        11,
        27,
        15,
        0,
        tzinfo=timezone.utc,
      ),
      "aqi": 1,
      "pm2_5": 0.9,
      "pm10": 0.93,
      "no2": 2.29,
      "o3": 46.49,
    }
  ]


def test_transform_empty_observations_returns_empty_list():
  raw_response = {
    "coord": {
      "lat": 50,
      "lon": 50,
    },
    "list": [],
  }

  location = {
    "city": "Paris",
    "country_code": "FR",
    "state": "",
  }

  assert transform_air_pollution(raw_response, location) == []


def test_transform_handles_missing_optional_pollutant():
  raw_response = {
    "coord": {
      "lat": 48.8566,
      "lon": 2.3522,
    },
    "list": [
      {
        "dt": 1606489200,
        "main": {"aqi": 2},
        "components": {
          "pm10": 10.5,
          "no2": 4.2,
          "o3": 40.0,
        },
      }
    ],
  }

  location = {
    "city": "Paris",
    "country_code": "FR",
    "state": "",
  }

  result = transform_air_pollution(raw_response, location)

  assert result[0]["location"] == "Paris, FR"
  assert result[0]["pm2_5"] is None


def test_transform_rejects_string_coordinates():
  raw_response = {
    "coord": {
      "lat": "50",
      "lon": "50",
    },
    "list": [
      {
        "dt": 1606489200,
        "main": {"aqi": 1},
        "components": {},
      }
    ],
  }

  location = {
    "city": "Paris",
    "country_code": "FR",
    "state": "",
  }

  with pytest.raises(
    ValueError,
    match="Latitude and longitude must be numeric",
  ):
    transform_air_pollution(raw_response, location)


def test_transform_rejects_out_of_range_longitude():
  raw_response = {
    "coord": {
      "lat": 50,
      "lon": 4000,
    },
    "list": [
      {
        "dt": 1606489200,
        "main": {"aqi": 1},
        "components": {},
      }
    ],
  }

  location = {
    "city": "Paris",
    "country_code": "FR",
    "state": "",
  }

  with pytest.raises(
    ValueError,
    match="Longitude is out of range",
  ):
    transform_air_pollution(raw_response, location)


def test_transform_multiple_observations():
  raw_response = {
      "coord": {
        "lat": 50,
        "lon": 50,
      },
      "list": [
        {
          "dt": 1606489200,
          "main": {"aqi": 1},
          "components": {
            "pm2_5": 0.9,
            "pm10": 0.93,
            "no2": 2.29,
            "o3": 46.49,
          },
        },
        {
          "dt": 1606492800,
          "main": {"aqi": 2},
          "components": {
            "pm2_5": 1.2,
            "pm10": 1.5,
            "no2": 3.1,
            "o3": 48.0,
          },
        },
      ],
  }

  location = {
    "city": "Raleigh",
    "country_code": "US",
    "state": "NC",
  }

  result = transform_air_pollution(raw_response, location)

  assert len(result) == 2
  assert result[0]["aqi"] == 1
  assert result[1]["aqi"] == 2
  assert result[0]["observed_at"] != result[1]["observed_at"]