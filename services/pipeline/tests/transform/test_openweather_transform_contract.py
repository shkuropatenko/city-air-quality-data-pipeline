"""Automated Transform Tests.

Tests for:
    services/pipeline/src/pipeline/transform/openweather.py

Based on the Sprint 3 transform contract, data dictionary, normalization
rules, and SCRUM-29 acceptance criteria.

The tests use sanitized OpenWeather samples only. They do not call the live
API and do not write to a database.
"""

from datetime import datetime, timezone
import pytest
from pipeline.transform.openweather import transform_air_pollution

@pytest.fixture
def location_context():
    return {
        "city": "Raleigh",
        "country_code": "US",
        "state": "NC",
    }

@pytest.fixture
def representative_raw_response():
    """Sanitized Sprint 2 OpenWeather Historical Air Pollution sample."""
    return {
        "coord": {
            "lon": 50,
            "lat": 50,
        },
        "list": [
            {
                "main": {
                    "aqi": 1,
                },
                "components": {
                    "co": 226.97,
                    "no": 0,
                    "no2": 2.29,
                    "o3": 46.49,
                    "so2": 0.95,
                    "pm2_5": 0.90,
                    "pm10": 0.93,
                    "nh3": 0.09,
                },
                "dt": 1606489200,
            }
        ],
    }

# main test
def test_transform_representative_successful_response(
    representative_raw_response,
    location_context,
):
    """A representative response must match the agreed clean contract."""
    records = transform_air_pollution(
        representative_raw_response,
        location_context,
    )

    assert isinstance(records, list)
    assert len(records) == 1

    record = records[0]

    assert set(record) == {
        "location",
        "latitude",
        "longitude",
        "observed_at",
        "aqi",
        "pm2_5",
        "pm10",
        "no2",
        "o3",
    }

    assert record["location"] == "Raleigh, US, NC"

    # Numeric types are normalized for the clean dataset.
    assert record["latitude"] == 50.0
    assert record["longitude"] == 50.0
    assert isinstance(record["latitude"], float)
    assert isinstance(record["longitude"], float)

    # Unix seconds are normalized to a timezone-aware UTC datetime.
    assert record["observed_at"] == datetime(
        2020,
        11,
        27,
        15,
        0,
        tzinfo=timezone.utc,
    )
    assert record["observed_at"].tzinfo == timezone.utc

    assert record["aqi"] == 1
    assert isinstance(record["aqi"], int)

    assert record["pm2_5"] == pytest.approx(0.90)
    assert record["pm10"] == pytest.approx(0.93)
    assert record["no2"] == pytest.approx(2.29)
    assert record["o3"] == pytest.approx(46.49)

    assert isinstance(record["pm2_5"], float)
    assert isinstance(record["pm10"], float)
    assert isinstance(record["no2"], float)
    assert isinstance(record["o3"], float)

# test for couple observations
def test_transform_supports_multiple_observations(
    representative_raw_response,
    location_context,
):
    """One clean record is returned for each distinct observation."""
    representative_raw_response["list"].append(
        {
            "main": {"aqi": 2},
            "components": {
                "pm2_5": 4.2,
                "pm10": 5.1,
                "no2": 3.3,
                "o3": 40.0,
            },
            "dt": 1606492800,
        }
    )

    records = transform_air_pollution(
        representative_raw_response,
        location_context,
    )

    assert len(records) == 2
    assert records[0]["observed_at"] != records[1]["observed_at"]
    assert records[1]["aqi"] == 2
    assert records[1]["pm2_5"] == pytest.approx(4.2)

# empty test
def test_transform_empty_response_returns_empty_list(location_context):
    """An empty observation list returns an empty clean result."""
    raw_response = {
        "coord": {
            "lon": -78.6382,
            "lat": 35.7796,
        },
        "list": [],
    }

    assert transform_air_pollution(raw_response, location_context) == []

# missed field
def test_transform_missing_optional_fields_are_none(location_context):
    """Missing optional pollutant fields do not reject the observation."""
    raw_response = {
        "coord": {
            "lon": -78.6382,
            "lat": 35.7796,
        },
        "list": [
            {
                "main": {"aqi": 2},
                "components": {
                    "pm2_5": 7.5,
                    # pm10, no2, and o3 intentionally omitted.
                },
                "dt": 1606489200,
            }
        ],
    }

    records = transform_air_pollution(raw_response, location_context)

    assert len(records) == 1
    assert records[0]["pm2_5"] == pytest.approx(7.5)
    assert records[0]["pm10"] is None
    assert records[0]["no2"] is None
    assert records[0]["o3"] is None

# Required fields tests
@pytest.mark.parametrize(
    "raw_response",
    [
        # Missing latitude.
        {
            "coord": {"lon": -78.6382},
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {},
                    "dt": 1606489200,
                }
            ],
        },
        # Missing longitude.
        {
            "coord": {"lat": 35.7796},
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {},
                    "dt": 1606489200,
                }
            ],
        },
        # Missing AQI.
        {
            "coord": {
                "lon": -78.6382,
                "lat": 35.7796,
            },
            "list": [
                {
                    "main": {},
                    "components": {},
                    "dt": 1606489200,
                }
            ],
        },
        # Missing timestamp.
        {
            "coord": {
                "lon": -78.6382,
                "lat": 35.7796,
            },
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {},
                }
            ],
        },
    ],
)

def test_transform_rejects_missing_required_fields(
    raw_response,
    location_context,
):
    """Missing fields required by the clean contract are rejected."""
    with pytest.raises((KeyError, ValueError, TypeError)):
        transform_air_pollution(raw_response, location_context)

# Malformed required fields tests
@pytest.mark.parametrize(
    "raw_response",
    [
        # Malformed latitude.
        {
            "coord": {
                "lon": -78.6382,
                "lat": "not-a-number",
            },
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {},
                    "dt": 1606489200,
                }
            ],
        },
        # Malformed longitude.
        {
            "coord": {
                "lon": "not-a-number",
                "lat": 35.7796,
            },
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {},
                    "dt": 1606489200,
                }
            ],
        },
        # Malformed AQI.
        {
            "coord": {
                "lon": -78.6382,
                "lat": 35.7796,
            },
            "list": [
                {
                    "main": {"aqi": "bad-aqi"},
                    "components": {},
                    "dt": 1606489200,
                }
            ],
        },
        # Malformed timestamp.
        {
            "coord": {
                "lon": -78.6382,
                "lat": 35.7796,
            },
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {},
                    "dt": "not-a-timestamp",
                }
            ],
        },
    ],
)

def test_transform_rejects_malformed_required_fields(
    raw_response,
    location_context,
):
    """Malformed required values must not silently enter clean data."""
    with pytest.raises((ValueError, TypeError)):
        transform_air_pollution(raw_response, location_context)

# Duplicates test
def test_transform_deduplicates_repeated_observations(location_context):
    """Repeated location/timestamp observations appear only once."""
    observation = {
        "main": {"aqi": 2},
        "components": {
            "pm2_5": 7.5,
            "pm10": 10.0,
            "no2": 4.5,
            "o3": 35.0,
        },
        "dt": 1606489200,
    }

    raw_response = {
        "coord": {
            "lon": -78.6382,
            "lat": 35.7796,
        },
        "list": [
            observation,
            observation.copy(),
        ],
    }

    records = transform_air_pollution(raw_response, location_context)

    assert len(records) == 1

# no state test
def test_transform_location_without_optional_state(representative_raw_response):
    """State is optional in the location context."""
    location = {
        "city": "Paris",
        "country_code": "FR",
    }

    records = transform_air_pollution(representative_raw_response, location)

    assert records[0]["location"] == "Paris, FR"