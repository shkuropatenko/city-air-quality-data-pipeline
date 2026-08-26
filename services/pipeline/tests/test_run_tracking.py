from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from pipeline.run_tracking import (
  INSERT_PIPELINE_RUN,
  UPDATE_PIPELINE_RUN,
  finish_pipeline_run,
  start_pipeline_run,
)

# check start pipeline run
def test_start_pipeline_run_creates_running_record():
  connection = Mock()
  result = Mock()

  result.scalar_one.return_value = 42
  connection.execute.return_value = result

  started_at = datetime(
    2026,
    8,
    25,
    12,
    0,
    tzinfo=timezone.utc,
  )

  run_id = start_pipeline_run(
    connection,
    started_at=started_at,
  )

  connection.execute.assert_called_once_with(
    INSERT_PIPELINE_RUN,
    {
      "started_at": started_at,
    },
  )

  assert run_id == 42

# check finish pipeline run / success
def test_finish_pipeline_run_records_success():
  connection = Mock()

  finished_at = datetime(
    2026,
    8,
    25,
    12,
    30,
    tzinfo=timezone.utc,
  )

  finish_pipeline_run(
    connection,
    run_id=42,
    status="success",
    records_processed=100,
    finished_at=finished_at,
  )

  connection.execute.assert_called_once_with(
    UPDATE_PIPELINE_RUN,
    {
      "run_id": 42,
      "finished_at": finished_at,
      "status": "success",
      "records_processed": 100,
      "error_message": None,
    },
  )

# check finish pipeline run / failure
def test_finish_pipeline_run_records_failure():
  connection = Mock()

  finished_at = datetime(
    2026,
    8,
    25,
    12,
    15,
    tzinfo=timezone.utc,
  )

  finish_pipeline_run(
    connection,
    run_id=42,
    status="failed",
    records_processed=25,
    error_message="database write failed",
    finished_at=finished_at,
  )

  connection.execute.assert_called_once_with(
    UPDATE_PIPELINE_RUN,
    {
      "run_id": 42,
      "finished_at": finished_at,
      "status": "failed",
      "records_processed": 25,
      "error_message": "database write failed",
    },
  )

# check finish pipeline run / invalid
def test_finish_pipeline_run_rejects_invalid_status():
  connection = Mock()

  with pytest.raises(
    ValueError,
    match="status must be",
  ):
    finish_pipeline_run(
      connection,
      run_id=42,
      status="unknown",
    )

  connection.execute.assert_not_called()

# check finish pipeline run / negative value
def test_finish_pipeline_run_rejects_negative_count():
  connection = Mock()

  with pytest.raises(
    ValueError,
    match="cannot be negative",
  ):
    finish_pipeline_run(
      connection,
      run_id=42,
      status="success",
      records_processed=-1,
    )

  connection.execute.assert_not_called()

# check finish pipeline run / unknown run_id
def test_finish_pipeline_run_rejects_unknown_run_id():
  connection = Mock()
  connection.execute.return_value.rowcount = 0

  with pytest.raises(
    ValueError,
    match="Pipeline run 999 was not found",
  ):
    finish_pipeline_run(
      connection,
      run_id=999,
      status="success",
    )