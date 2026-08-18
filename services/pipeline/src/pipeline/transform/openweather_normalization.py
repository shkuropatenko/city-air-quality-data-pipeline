import logging
import math
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


def _log_invalid(field, value):
    logger.warning("Invalid or missing normalization value: field=%s value=%r", field, value)


def normalize_number(value, field):
    if value is None or isinstance(value, bool):
        _log_invalid(field, value)
        return None

    try:
        normalized = float(value)
    except (TypeError, ValueError):
        _log_invalid(field, value)
        return None

    if not math.isfinite(normalized):
        _log_invalid(field, value)
        return None

    return normalized


def normalize_timestamp(value, field):
    normalized = normalize_number(value, field)

    if normalized is None:
        return None

    if not normalized.is_integer():
        _log_invalid(field, value)
        return None

    try:
        return datetime.fromtimestamp(normalized, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        _log_invalid(field, value)
        return None


def normalize_aqi(value, field):
    normalized = normalize_number(value, field)

    if normalized is None:
        return None

    if not normalized.is_integer():
        _log_invalid(field, value)
        return None

    normalized = int(normalized)

    if normalized not in range(1, 6):
        _log_invalid(field, value)
        return None

    return normalized
