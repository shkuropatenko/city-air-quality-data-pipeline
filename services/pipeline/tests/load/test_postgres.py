from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from pipeline.load.postgres import (
  INSERT_AIR_QUALITY_RECORDS,
  INSERT_RAW_API_RESPONSE,
  prepare_air_quality_values,
  save_raw_response,
  save_transformed_records,
)


def test_prepare_air_quality_values_selects_database_record_fields():
  observed_at = datetime(2020, 11, 27, 13, 0, tzinfo=timezone.utc)
  transformed_record = {
    "location": "Charlotte, US, NC",
    "latitude": 35.2271,
    "longitude": -80.8431,
    "observed_at": observed_at,
    "aqi": 2,
    "pm2_5": 13.448,
    "pm10": 15.524,
    "no2": 43.184,
    "o3": 4.783,
  }

  values = prepare_air_quality_values(transformed_record)

  assert values == {
    "observed_at": observed_at,
    "aqi": 2,
    "pm2_5": 13.448,
    "pm10": 15.524,
    "no2": 43.184,
    "o3": 4.783,
  }


def test_prepare_air_quality_values_maps_missing_optional_pollutants_to_none():
  observed_at = datetime(2020, 11, 27, 13, 0, tzinfo=timezone.utc)
  transformed_record = {
    "location": "Charlotte, US, NC",
    "latitude": 35.2271,
    "longitude": -80.8431,
    "observed_at": observed_at,
    "aqi": 2,
  }

  values = prepare_air_quality_values(transformed_record)

  assert values == {
    "observed_at": observed_at,
    "aqi": 2,
    "pm2_5": None,
    "pm10": None,
    "no2": None,
    "o3": None,
  }


def test_air_quality_upsert_uses_record_key_and_updates_measurements():
  statement = str(
    INSERT_AIR_QUALITY_RECORDS.compile(dialect=postgresql.dialect())
  )
  normalized_statement = " ".join(statement.split())

  assert "ON CONFLICT (location_id, observed_at) DO UPDATE" in normalized_statement
  update_clause = normalized_statement.split("DO UPDATE SET ", 1)[1]
  expected_assignments = (
    "aqi = excluded.aqi",
    "pm2_5 = excluded.pm2_5",
    "pm10 = excluded.pm10",
    "no2 = excluded.no2",
    "o3 = excluded.o3",
  )
  for assignment in expected_assignments:
    assert assignment in update_clause
  assert "location_id =" not in update_clause
  assert "observed_at =" not in update_clause


def test_save_transformed_records_inserts_one_observation():
  connection = Mock()
  observed_at = datetime(2020, 11, 27, 13, 0, tzinfo=timezone.utc)
  record = {
    "location": "Charlotte, US, NC",
    "latitude": 35.2271,
    "longitude": -80.8431,
    "observed_at": observed_at,
    "aqi": 2,
  }

  save_transformed_records(connection, location_id=42, records=[record])

  connection.execute.assert_called_once_with(INSERT_AIR_QUALITY_RECORDS, [{
    "location_id": 42,
    "observed_at": observed_at,
    "aqi": 2,
    "pm2_5": None,
    "pm10": None,
    "no2": None,
    "o3": None,
  }])


def test_save_transformed_records_inserts_multiple_observations():
  connection = Mock()
  first_observed_at = datetime(2020, 11, 27, 13, 0, tzinfo=timezone.utc)
  second_observed_at = datetime(2020, 11, 27, 14, 0, tzinfo=timezone.utc)
  records = [
    {
      "observed_at": first_observed_at,
      "aqi": 2,
      "pm2_5": 13.448,
      "pm10": 15.524,
      "no2": 43.184,
      "o3": 4.783,
    },
    {
      "observed_at": second_observed_at,
      "aqi": 3,
      "pm2_5": 18.2,
      "pm10": 21.1,
      "no2": 37.5,
      "o3": 8.4,
    },
  ]

  save_transformed_records(connection, location_id=42, records=records)

  connection.execute.assert_called_once_with(INSERT_AIR_QUALITY_RECORDS, [
    {
      "location_id": 42,
      **prepare_air_quality_values(records[0]),
    },
    {
      "location_id": 42,
      **prepare_air_quality_values(records[1]),
    },
  ])


def test_save_transformed_records_does_not_execute_for_empty_records():
  connection = Mock()

  save_transformed_records(connection, location_id=42, records=[])

  connection.execute.assert_not_called()


def test_save_transformed_records_propagates_database_error():
  connection = Mock()
  connection.execute.side_effect = SQLAlchemyError("database write failed")
  record = {
    "observed_at": datetime(2020, 11, 27, 13, 0, tzinfo=timezone.utc),
    "aqi": 2,
  }

  with pytest.raises(SQLAlchemyError, match="database write failed"):
    save_transformed_records(connection, location_id=42, records=[record])


def test_save_raw_response_inserts_complete_payload():
  connection = Mock()
  fetched_at = datetime(2020, 11, 27, 15, 0, tzinfo=timezone.utc)
  payload = {
    "coord": {"lat": 35.2271, "lon": -80.8431},
    "list": [{
      "dt": 1606489200,
      "main": {"aqi": 2},
      "components": {"pm2_5": 13.448, "pm10": 15.524},
    }],
  }

  save_raw_response(connection, location_id=42, fetched_at=fetched_at, payload=payload)

  connection.execute.assert_called_once_with(INSERT_RAW_API_RESPONSE, {
    "location_id": 42,
    "fetched_at": fetched_at,
    "payload": payload,
  })


def test_save_raw_response_propagates_database_error():
  connection = Mock()
  connection.execute.side_effect = SQLAlchemyError("database write failed")

  with pytest.raises(SQLAlchemyError, match="database write failed"):
    save_raw_response(
      connection,
      location_id=42,
      fetched_at=datetime(2020, 11, 27, 15, 0, tzinfo=timezone.utc),
      payload={"coord": {"lat": 35.2271, "lon": -80.8431}, "list": []},
    )
