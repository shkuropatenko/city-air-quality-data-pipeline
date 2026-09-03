import logging
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

logger = logging.getLogger(__name__)


def run_pipeline(
    connection: Connection,
    locations: list[dict],
    start: int,
    end: int,
) -> dict:
    run_id = start_pipeline_run(connection)
    records_processed = 0
    errors = []

    logger.info(
        "Pipeline started: run_id=%s locations=%d start=%s end=%s",
        run_id,
        len(locations),
        start,
        end,
    )

    for location in locations:

        city = location.get("city", "unknown")
        stage = "extract"

        try:
            with connection.begin_nested():

                logger.info(
                    "Stage started: run_id=%s city=%s stage=%s",
                    run_id,
                    city,
                    stage,
                )

                coords = geocode_location(location)

                raw_response = fetch_air_pollution_history(
                    coords["lat"],
                    coords["lon"],
                    start,
                    end,
                )

                logger.info(
                    "Stage completed: run_id=%s city=%s stage=%s",
                    run_id,
                    city,
                    stage,
                )

                stage = "raw_persistence"

                logger.info(
                    "Stage started: run_id=%s city=%s stage=%s",
                    run_id,
                    city,
                    stage,
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

                logger.info(
                    "Stage completed: run_id=%s city=%s stage=%s",
                    run_id,
                    city,
                    stage,
                )

                stage = "transform"

                logger.info(
                    "Stage started: run_id=%s city=%s stage=%s",
                    run_id,
                    city,
                    stage,
                )

                records = transform_air_pollution(
                    raw_response,
                    location,
                )

                logger.info(
                    "Stage completed: run_id=%s city=%s stage=%s records=%d",
                    run_id,
                    city,
                    stage,
                    len(records),
                )

                stage = "load"

                logger.info(
                    "Stage started: run_id=%s city=%s stage=%s",
                    run_id,
                    city,
                    stage,
                )

                save_transformed_records(
                    connection,
                    location_id,
                    records,
                )

                logger.info(
                    "Stage completed: run_id=%s city=%s stage=%s records=%d",
                    run_id,
                    city,
                    stage,
                    len(records),
                )

                records_processed += len(records)

        except Exception as exc:
            logger.exception(
                "Stage failed: run_id=%s city=%s stage=%s error=%s",
                run_id,
                city,
                stage,
                exc,
            )
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

    if errors:
        logger.error(
            "Pipeline failed: run_id=%s records_processed=%d errors=%d",
            run_id,
            records_processed,
            len(errors),
        )
    else:
        logger.info(
            "Pipeline succeeded: run_id=%s records_processed=%d",
            run_id,
            records_processed,
        )

    return {
        "run_id": run_id,
        "status": status,
        "records_processed": records_processed,
        "errors": errors,
    }
