import logging
from datetime import datetime, timezone

import pytest

from pipeline.transform.openweather_normalization import (
    normalize_aqi,
    normalize_number,
    normalize_timestamp,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (13.448, 13.448),
        (0, 0.0),
        ("15.524", 15.524),
    ],
)
def test_normalize_number_returns_float(value, expected):
    assert normalize_number(value, "components.pm2_5") == expected


@pytest.mark.parametrize("value", [None, "not-a-number", float("nan"), float("inf"), True])
def test_normalize_number_returns_none_and_logs_invalid_value(value, caplog):
    with caplog.at_level(logging.WARNING, logger="pipeline.transform.openweather_normalization"):
        result = normalize_number(value, "components.pm2_5")

    assert result is None
    assert "field=components.pm2_5" in caplog.text
    assert f"value={value!r}" in caplog.text


def test_normalize_timestamp_returns_timezone_aware_utc_datetime():
    result = normalize_timestamp("1606482000", "dt")

    assert result == datetime(2020, 11, 27, 13, 0, tzinfo=timezone.utc)
    assert result.tzinfo is timezone.utc


@pytest.mark.parametrize("value", [None, "bad-timestamp", 1606482000.5])
def test_normalize_timestamp_returns_none_for_invalid_value(value, caplog):
    with caplog.at_level(logging.WARNING, logger="pipeline.transform.openweather_normalization"):
        result = normalize_timestamp(value, "dt")

    assert result is None
    assert "field=dt" in caplog.text
    assert f"value={value!r}" in caplog.text


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1, 1), ("5", 5), (2.0, 2), ("2.0", 2)],
)
def test_normalize_aqi_accepts_openweather_range(value, expected):
    assert normalize_aqi(value, "main.aqi") == expected


@pytest.mark.parametrize("value", [None, "bad-aqi", 0, 6, 2.5])
def test_normalize_aqi_returns_none_for_invalid_or_out_of_range_value(value, caplog):
    with caplog.at_level(logging.WARNING, logger="pipeline.transform.openweather_normalization"):
        result = normalize_aqi(value, "main.aqi")

    assert result is None
    assert "field=main.aqi" in caplog.text
    assert f"value={value!r}" in caplog.text
