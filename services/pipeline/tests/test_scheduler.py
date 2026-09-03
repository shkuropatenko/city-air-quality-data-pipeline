import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest

from pipeline.orchestration import scheduler
from pipeline.extract.location_validation import LocationValidationError


def test_historical_window_returns_configured_utc_unix_range():
  controlled_now = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)

  with patch.object(scheduler, "datetime") as datetime_mock:
    datetime_mock.now.return_value = controlled_now
    start, end = scheduler._historical_window(24)

  datetime_mock.now.assert_called_once_with(timezone.utc)
  assert isinstance(start, int)
  assert isinstance(end, int)
  assert end == int(controlled_now.timestamp())
  assert end - start == 24 * 60 * 60


def test_history_hours_returns_positive_integer():
  with patch.dict(
    os.environ,
    {"PIPELINE_HISTORY_HOURS": "24"},
    clear=True,
  ):
    assert scheduler._history_hours() == 24


@pytest.mark.parametrize(
  ("value", "expected_message"),
  [
    (None, "PIPELINE_HISTORY_HOURS is required"),
    ("0", "must be a positive integer"),
    ("-1", "must be a positive integer"),
    ("not-a-number", "must be a positive integer"),
  ],
)
def test_history_hours_rejects_missing_or_invalid_values(
  monkeypatch,
  value,
  expected_message,
):
  if value is None:
    monkeypatch.delenv("PIPELINE_HISTORY_HOURS", raising=False)
  else:
    monkeypatch.setenv("PIPELINE_HISTORY_HOURS", value)

  with pytest.raises(ValueError, match=expected_message):
    scheduler._history_hours()


def test_valid_locations_returns_valid_rows_despite_validation_errors():
  raw_records = [
    {"city": "Charlotte", "country_code": "US", "state": "NC"},
    {"city": "", "country_code": "US", "state": ""},
  ]
  valid_locations = [
    {"city": "Charlotte", "country_code": "US", "state": "NC"},
  ]
  validation_errors = [
    LocationValidationError(3, "Missing required field: city", raw_records[1]),
  ]

  with (
    patch.object(scheduler, "read_city_records", return_value=raw_records) as read,
    patch.object(
      scheduler,
      "validate_city_records",
      return_value=(valid_locations, validation_errors),
    ) as validate,
  ):
    result = scheduler._valid_locations()

  read.assert_called_once_with()
  validate.assert_called_once_with(raw_records)
  assert result == valid_locations


def test_valid_locations_rejects_empty_valid_result_with_error_context():
  raw_records = [{"city": "", "country_code": "US", "state": ""}]
  validation_errors = [
    LocationValidationError(2, "Missing required field: city", raw_records[0]),
  ]

  with (
    patch.object(scheduler, "read_city_records", return_value=raw_records),
    patch.object(
      scheduler,
      "validate_city_records",
      return_value=([], validation_errors),
    ),
    pytest.raises(
      ValueError,
      match="No valid locations are configured: row 2: Missing required field: city",
    ),
  ):
    scheduler._valid_locations()


def test_run_scheduled_pipeline_calls_runner_in_transaction_and_returns_success(
  monkeypatch,
):
  monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://example")
  locations = [{"city": "Charlotte", "country_code": "US", "state": "NC"}]
  expected_result = {
    "run_id": 42,
    "status": "success",
    "records_processed": 3,
    "errors": [],
  }
  engine = MagicMock()
  connection = Mock()
  engine.begin.return_value.__enter__.return_value = connection

  with (
    patch.object(scheduler, "load_dotenv") as load_dotenv,
    patch.object(scheduler, "_valid_locations", return_value=locations),
    patch.object(scheduler, "_history_hours", return_value=24),
    patch.object(scheduler, "_historical_window", return_value=(100, 200)),
    patch.object(scheduler, "create_engine", return_value=engine) as create_engine,
    patch.object(scheduler, "run_pipeline", return_value=expected_result) as runner,
  ):
    result = scheduler.run_scheduled_pipeline()

  load_dotenv.assert_called_once_with()
  create_engine.assert_called_once_with("postgresql+psycopg://example")
  engine.begin.assert_called_once_with()
  engine.begin.return_value.__enter__.assert_called_once_with()
  engine.begin.return_value.__exit__.assert_called_once_with(None, None, None)
  runner.assert_called_once_with(connection, locations, 100, 200)
  engine.dispose.assert_called_once_with()
  assert result == expected_result


def test_run_scheduled_pipeline_commits_before_surfacing_failed_result(monkeypatch):
  monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://example")
  events = []
  connection = Mock()

  class Transaction:
    def __enter__(self):
      events.append("transaction entered")
      return connection

    def __exit__(self, exc_type, exc_value, traceback):
      events.append("transaction exited")

  engine = Mock()
  engine.begin.return_value = Transaction()
  engine.dispose.side_effect = lambda: events.append("engine disposed")
  failed_result = {
    "run_id": 42,
    "status": "failed",
    "records_processed": 0,
    "errors": ["Charlotte: request failed"],
  }

  with (
    patch.object(scheduler, "load_dotenv"),
    patch.object(scheduler, "_valid_locations", return_value=[{"city": "Charlotte"}]),
    patch.object(scheduler, "_history_hours", return_value=24),
    patch.object(scheduler, "_historical_window", return_value=(100, 200)),
    patch.object(scheduler, "create_engine", return_value=engine),
    patch.object(scheduler, "run_pipeline", return_value=failed_result),
    pytest.raises(RuntimeError, match="Scheduled pipeline failed.*Charlotte"),
  ):
    scheduler.run_scheduled_pipeline()

  assert events == [
    "transaction entered",
    "transaction exited",
    "engine disposed",
  ]


def test_run_scheduled_pipeline_propagates_runner_error_and_disposes_engine(monkeypatch):
  monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://example")
  engine = MagicMock()
  connection = Mock()
  engine.begin.return_value.__enter__.return_value = connection

  with (
    patch.object(scheduler, "load_dotenv"),
    patch.object(scheduler, "_valid_locations", return_value=[{"city": "Charlotte"}]),
    patch.object(scheduler, "_history_hours", return_value=24),
    patch.object(scheduler, "_historical_window", return_value=(100, 200)),
    patch.object(scheduler, "create_engine", return_value=engine),
    patch.object(
      scheduler,
      "run_pipeline",
      side_effect=RuntimeError("runner crashed"),
    ),
    pytest.raises(RuntimeError, match="runner crashed"),
  ):
    scheduler.run_scheduled_pipeline()

  engine.dispose.assert_called_once_with()


def test_main_serves_configured_cron_schedule_in_utc(monkeypatch):
  monkeypatch.setenv("PIPELINE_SCHEDULE_CRON", "15 * * * *")

  with (
    patch.object(scheduler, "load_dotenv") as load_dotenv,
    patch.object(scheduler.scheduled_pipeline_flow, "serve") as serve,
  ):
    scheduler.main()

  load_dotenv.assert_called_once_with()
  serve.assert_called_once()
  assert serve.call_args.kwargs["name"] == scheduler.FLOW_NAME
  schedule = serve.call_args.kwargs["schedule"]
  assert schedule.cron == "15 * * * *"
  assert schedule.timezone == "UTC"


def test_main_requires_cron_configuration(monkeypatch):
  monkeypatch.delenv("PIPELINE_SCHEDULE_CRON", raising=False)

  with (
    patch.object(scheduler, "load_dotenv"),
    patch.object(scheduler.scheduled_pipeline_flow, "serve") as serve,
    pytest.raises(ValueError, match="PIPELINE_SCHEDULE_CRON is required"),
  ):
    scheduler.main()

  serve.assert_not_called()
