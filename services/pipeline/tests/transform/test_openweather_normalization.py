from datetime import datetime, timezone

from pipeline.transform.openweather_normalization import (
  normalize_aqi,
  normalize_number,
  normalize_timestamp,
)


def test_normalize_number():
  assert normalize_number(10) == 10.0
  assert normalize_number("12.5") == 12.5
  assert normalize_number(None) is None
  assert normalize_number("invalid") is None


def test_normalize_aqi():
  assert normalize_aqi(1) == 1
  assert normalize_aqi("5") == 5

  assert normalize_aqi(0) is None
  assert normalize_aqi(6) is None
  assert normalize_aqi("invalid") is None


def test_normalize_timestamp():
  result = normalize_timestamp(1606489200)

  assert result == datetime(
    2020,
    11,
    27,
    15,
    0,
    tzinfo=timezone.utc,
  )

  assert normalize_timestamp(None) is None
  assert normalize_timestamp("invalid") is None