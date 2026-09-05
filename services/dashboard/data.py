from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.engine import Connection

from services.database.models import AirQualityRecord, Location

def _serialize_location(row: Mapping[str, Any]) -> dict:
  return {
    "id": row["id"],
    "city": row["city"],
    "country_code": row["country_code"],
    "state": row["state"],
    "latitude": row["latitude"],
    "longitude": row["longitude"],
  }


def _serialize_observation(row: Mapping[str, Any]) -> dict:
  observed_at: datetime = row["observed_at"]
  observed_at_utc = observed_at.astimezone(timezone.utc)

  return {
    "observed_at": observed_at_utc.isoformat().replace("+00:00", "Z"),
    "aqi": row["aqi"],
    "pm2_5": row["pm2_5"],
    "pm10": row["pm10"],
    "no2": row["no2"],
    "o3": row["o3"],
  }


def get_available_locations(connection: Connection) -> dict:
  statement = (
      select(
        Location.id,
        Location.city,
        Location.country_code,
        Location.state,
        Location.latitude,
        Location.longitude,
      )
      .order_by(
        Location.city.asc(),
        Location.country_code.asc(),
        Location.state.asc().nulls_first(),
        Location.id.asc(),
      )
  )

  rows = connection.execute(statement).mappings().all()
  return {"locations": [_serialize_location(row) for row in rows]}


def get_location_observations(
    connection: Connection,
    location_id: int,
) -> dict | None:
  location_statement = select(
    Location.id,
    Location.city,
    Location.country_code,
    Location.state,
    Location.latitude,
    Location.longitude,
  ).where(Location.id == location_id)

  location = connection.execute(location_statement).mappings().one_or_none()
  if location is None:
    return None

  observations_statement = (
    select(
      AirQualityRecord.observed_at,
      AirQualityRecord.aqi,
      AirQualityRecord.pm2_5,
      AirQualityRecord.pm10,
      AirQualityRecord.no2,
      AirQualityRecord.o3,
    )
    .where(AirQualityRecord.location_id == location_id)
    .order_by(
      AirQualityRecord.observed_at.asc(),
      AirQualityRecord.id.asc(),
    )
  )

  observations = (
    connection.execute(observations_statement).mappings().all()
  )

  return {
    "location": _serialize_location(location),
    "observations": [
      _serialize_observation(observation)
      for observation in observations
    ],
  }
