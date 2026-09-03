from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.engine import Connection

from services.database.models import (
    AirQualityRecord,
    Location,
    RawApiResponse,
)


_air_quality_insert = postgresql_insert(AirQualityRecord)
INSERT_AIR_QUALITY_RECORDS = _air_quality_insert.on_conflict_do_update(
    index_elements=["location_id", "observed_at"],
    set_={
        "aqi": _air_quality_insert.excluded.aqi,
        "pm2_5": _air_quality_insert.excluded.pm2_5,
        "pm10": _air_quality_insert.excluded.pm10,
        "no2": _air_quality_insert.excluded.no2,
        "o3": _air_quality_insert.excluded.o3,
    },
)

INSERT_RAW_API_RESPONSE = insert(RawApiResponse)


def prepare_air_quality_values(record):
    """Select transformed values stored in an air quality record row."""
    return {
        "observed_at": record["observed_at"],
        "aqi": record["aqi"],
        "pm2_5": record.get("pm2_5"),
        "pm10": record.get("pm10"),
        "no2": record.get("no2"),
        "o3": record.get("o3"),
    }

def resolve_location_id(
    connection: Connection,
    location: dict,
    latitude: float,
    longitude: float,
) -> int:
    """Create or find a location and return its database id."""

    statement = postgresql_insert(Location).values(
        city=location["city"],
        country_code=location["country_code"],
        state=location.get("state") or None,
        latitude=latitude,
        longitude=longitude,
    )

    statement = statement.on_conflict_do_update(
        index_elements=[
            "city",
            "country_code",
            "latitude",
            "longitude",
        ],
        set_={
            "state": statement.excluded.state,
        },
    ).returning(Location.id)

    return connection.execute(statement).scalar_one()

def save_transformed_records(
    connection: Connection,
    location_id: int,
    records: list[dict],
) -> None:
    """Insert transformed observations for an already-resolved location."""
    values = [
        {
            "location_id": location_id,
            **prepare_air_quality_values(record),
        }
        for record in records
    ]

    if not values:
        return

    connection.execute(INSERT_AIR_QUALITY_RECORDS, values)


def save_raw_response(
    connection: Connection,
    location_id: int,
    fetched_at: datetime,
    payload: dict,
) -> None:
    """Insert a complete raw API response for an already-resolved location."""
    connection.execute(INSERT_RAW_API_RESPONSE, {
        "location_id": location_id,
        "fetched_at": fetched_at,
        "payload": payload,
    })
