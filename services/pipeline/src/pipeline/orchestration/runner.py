from datetime import datetime, timezone

from sqlalchemy.engine import Connection

from pipeline.extract.openweather import (
  fetch_air_pollution_history,
  geocode_location,
)
from pipeline.load.postgres import (
  resolve_location_id,
  save_raw_response,
  save_transformed_records,
)
from pipeline.run_tracking import (
  finish_pipeline_run,
  start_pipeline_run,
)
from pipeline.transform.openweather import transform_air_pollution


def run_pipeline(
  connection: Connection,
  locations: list[dict],
  start: int,
  end: int,
) -> dict:
  run_id = start_pipeline_run(connection)
  records_processed = 0
  errors = []

  for location in locations:
    try:
      coords = geocode_location(location)

      raw_response = fetch_air_pollution_history(
        coords["lat"],
        coords["lon"],
        start,
        end,
      )

      location_id = resolve_location_id(
        connection,
        location,
        coords["lat"],
        coords["lon"],
      )

      save_raw_response(
        connection,
        location_id,
        datetime.now(timezone.utc),
        raw_response,
      )

      records = transform_air_pollution(
        raw_response,
        location,
      )

      save_transformed_records(
        connection,
        location_id,
        records,
      )

      records_processed += len(records)

    except Exception as exc:
        city = location.get("city", "unknown")
        errors.append(f"{city}: {exc}")
        continue

  status = "failed" if errors else "success"

  finish_pipeline_run(
    connection,
    run_id,
    status,
    records_processed=records_processed,
    error_message="; ".join(errors) if errors else None,
  )

  return {
    "run_id": run_id,
    "status": status,
    "records_processed": records_processed,
    "errors": errors,
  }