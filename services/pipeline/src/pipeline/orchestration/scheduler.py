import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from prefect import flow
from prefect.schedules import Cron
from sqlalchemy import create_engine

from pipeline.extract.location_input import read_city_records
from pipeline.extract.location_validation import validate_city_records
from pipeline.orchestration.runner import run_pipeline


FLOW_NAME = "city-air-tracker-scheduled-pipeline"


def _required_environment_value(name: str) -> str:
	value = os.getenv(name)
	if not value:
		raise ValueError(f"{name} is required")
	return value


def _history_hours() -> int:
	raw_value = _required_environment_value("PIPELINE_HISTORY_HOURS")

	try:
		hours = int(raw_value)
	except ValueError as exc:
		raise ValueError("PIPELINE_HISTORY_HOURS must be a positive integer") from exc

	if hours <= 0:
		raise ValueError("PIPELINE_HISTORY_HOURS must be a positive integer")

	return hours


def _historical_window(history_hours: int) -> tuple[int, int]:
	end_utc = datetime.now(timezone.utc)
	start_utc = end_utc - timedelta(hours=history_hours)
	return int(start_utc.timestamp()), int(end_utc.timestamp())


def _valid_locations() -> list[dict[str, str]]:
	records = read_city_records()
	locations, validation_errors = validate_city_records(records)

	if locations:
		return locations

	error_details = "; ".join(
		f"row {error.row_number}: {error.message}"
		for error in validation_errors
	)
	message = "No valid locations are configured"
	if error_details:
		message = f"{message}: {error_details}"
	raise ValueError(message)


def run_scheduled_pipeline() -> dict:
	"""Prepare runtime inputs and execute one scheduled pipeline run."""
	load_dotenv()

	database_url = _required_environment_value("DATABASE_URL")
	locations = _valid_locations()
	start, end = _historical_window(_history_hours())
	engine = create_engine(database_url)

	try:
		with engine.begin() as connection:
				result = run_pipeline(connection, locations, start, end)
	finally:
		engine.dispose()

	if not isinstance(result, dict):
		raise RuntimeError("Scheduled pipeline returned an invalid result")

	if result.get("status") != "success":
		raise RuntimeError(f"Scheduled pipeline failed: {result}")

	return result


@flow(name=FLOW_NAME)
def scheduled_pipeline_flow() -> dict:
	"""Prefect flow for one scheduled City Air Tracker pipeline run."""
	return run_scheduled_pipeline()


def main() -> None:
	load_dotenv()
	cron = _required_environment_value("PIPELINE_SCHEDULE_CRON")
	scheduled_pipeline_flow.serve(
		name=FLOW_NAME,
		schedule=Cron(cron, timezone="UTC"),
	)


if __name__ == "__main__":
	main()
