"""SCRUM-29 - Automated Transform Tests.

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


# Main clean-contract test
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

    # Coordinates are validated by the transform.
    assert record["latitude"] == 50
    assert record["longitude"] == 50

    # SCRUM-26 normalization converts Unix seconds to aware UTC datetime.
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


# Multiple observations
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


# Empty response
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


# Missing optional fields
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


# Missing required coordinates
@pytest.mark.parametrize(
    "coord",
    [
        {"lon": -78.6382},
        {"lat": 35.7796},
    ],
)
def test_transform_rejects_missing_coordinates(
    coord,
    location_context,
):
    """Missing required coordinates raise the transform's defined ValueError."""
    raw_response = {
        "coord": coord,
        "list": [
            {
                "main": {"aqi": 2},
                "components": {},
                "dt": 1606489200,
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match="Latitude and longitude must be numeric",
    ):
        transform_air_pollution(raw_response, location_context)


# Malformed required coordinates
@pytest.mark.parametrize(
    "coord",
    [
        {
            "lon": -78.6382,
            "lat": "not-a-number",
        },
        {
            "lon": "not-a-number",
            "lat": 35.7796,
        },
    ],
)
def test_transform_rejects_malformed_coordinates(
    coord,
    location_context,
):
    """Malformed coordinates raise the transform's defined ValueError."""
    raw_response = {
        "coord": coord,
        "list": [
            {
                "main": {"aqi": 2},
                "components": {},
                "dt": 1606489200,
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match="Latitude and longitude must be numeric",
    ):
        transform_air_pollution(raw_response, location_context)


# Missing required observation fields
@pytest.mark.parametrize(
    "item",
    [
        {
            "main": {},
            "components": {},
            "dt": 1606489200,
        },
        {
            "main": {"aqi": 2},
            "components": {},
        },
    ],
)
def test_transform_skips_missing_required_observation_fields(
    item,
    location_context,
):
    """Observations missing required AQI or timestamp are skipped safely."""
    raw_response = {
        "coord": {
            "lon": -78.6382,
            "lat": 35.7796,
        },
        "list": [item],
    }

    assert transform_air_pollution(raw_response, location_context) == []


# Malformed/invalid required observation values
@pytest.mark.parametrize(
    "item",
    [
        {
            "main": {"aqi": "bad-aqi"},
            "components": {},
            "dt": 1606489200,
        },
        {
            "main": {"aqi": 6},
            "components": {},
            "dt": 1606489200,
        },
        {
            "main": {"aqi": 2},
            "components": {},
            "dt": "not-a-timestamp",
        },
    ],
)
def test_transform_skips_malformed_required_observation_values(
    item,
    location_context,
):
    """Malformed or invalid required observation values are skipped safely."""
    raw_response = {
        "coord": {
            "lon": -78.6382,
            "lat": 35.7796,
        },
        "list": [item],
    }

    assert transform_air_pollution(raw_response, location_context) == []


# Repeated records/timestamps
def test_transform_deduplicates_repeated_observations(location_context):
    """Repeated location/timestamp observations should appear only once."""
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


# Optional state
def test_transform_location_without_optional_state(
    representative_raw_response,
):
    """State is optional in the location context."""
    location = {
        "city": "Paris",
        "country_code": "FR",
    }

    records = transform_air_pollution(
        representative_raw_response,
        location,
    )

    assert records[0]["location"] == "Paris, FR"