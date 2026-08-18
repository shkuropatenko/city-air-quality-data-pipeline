from datetime import datetime, timezone


def normalize_number(value):
  if value is None:
    return None

  try:
    return float(value)
  except (TypeError, ValueError):
    return None


def normalize_timestamp(value):
  if value is None:
    return None

  try:
    timestamp = int(value)
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
  except (TypeError, ValueError, OSError, OverflowError):
    return None


def normalize_aqi(value):
  if value is None:
    return None

  try:
    aqi = int(value)
  except (TypeError, ValueError):
    return None

  if not 1 <= aqi <= 5:
    return None

  return aqi