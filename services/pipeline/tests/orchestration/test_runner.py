from unittest.mock import MagicMock, call, patch

from pipeline.orchestration.runner import run_pipeline


@patch("pipeline.orchestration.runner.finish_pipeline_run")
@patch("pipeline.orchestration.runner.start_pipeline_run")
@patch("pipeline.orchestration.runner.save_transformed_records")
@patch("pipeline.orchestration.runner.save_raw_response")
@patch("pipeline.orchestration.runner.resolve_location_id")
@patch("pipeline.orchestration.runner.transform_air_pollution")
@patch("pipeline.orchestration.runner.fetch_air_pollution_history")
@patch("pipeline.orchestration.runner.geocode_location")
def test_run_pipeline_success(
    mock_geocode,
    mock_fetch,
    mock_transform,
    mock_resolve_location,
    mock_save_raw,
    mock_save_records,
    mock_start_run,
    mock_finish_run,
):
    connection = MagicMock()

    locations = [
        {
            "city": "New York",
            "country_code": "US",
        }
    ]

    mock_start_run.return_value = 1
    mock_geocode.return_value = {
        "lat": 40.7128,
        "lon": -74.0060,
    }

    raw_response = {"list": [{"dt": 1234567890}]}
    mock_fetch.return_value = raw_response

    records = [
        {
            "city": "New York",
            "aqi": 2,
        }
    ]
    mock_transform.return_value = records
    mock_resolve_location.return_value = 10

    stage_calls = MagicMock()

    stage_calls.attach_mock(mock_geocode, "geocode")
    stage_calls.attach_mock(mock_fetch, "fetch")
    stage_calls.attach_mock(mock_transform, "transform")
    stage_calls.attach_mock(mock_save_records, "load")

    result = run_pipeline(
        connection,
        locations,
        start=100,
        end=200,
    )

    assert stage_calls.mock_calls == [
        call.geocode(locations[0]),
        call.fetch(
            40.7128,
            -74.0060,
            100,
            200,
        ),
        call.transform(
            raw_response,
            locations[0],
        ),
        call.load(
            connection,
            10,
            records,
        ),
    ]

    assert result["run_id"] == 1
    assert result["status"] == "success"
    assert result["records_processed"] == 1
    assert result["errors"] == []

    mock_geocode.assert_called_once_with(locations[0])

    mock_fetch.assert_called_once_with(
        40.7128,
        -74.0060,
        100,
        200,
    )

    mock_transform.assert_called_once_with(
        raw_response,
        locations[0],
    )

    mock_resolve_location.assert_called_once_with(
        connection,
        locations[0],
        40.7128,
        -74.0060,
    )

    mock_save_records.assert_called_once_with(
        connection,
        10,
        records,
    )

    mock_finish_run.assert_called_once_with(
        connection,
        1,
        "success",
        records_processed=1,
        error_message=None,
    )

@patch("pipeline.orchestration.runner.finish_pipeline_run")
@patch("pipeline.orchestration.runner.start_pipeline_run")
@patch("pipeline.orchestration.runner.save_transformed_records")
@patch("pipeline.orchestration.runner.save_raw_response")
@patch("pipeline.orchestration.runner.resolve_location_id")
@patch("pipeline.orchestration.runner.transform_air_pollution")
@patch("pipeline.orchestration.runner.fetch_air_pollution_history")
@patch("pipeline.orchestration.runner.geocode_location")
def test_run_pipeline_continues_after_location_failure(
    mock_geocode,
    mock_fetch,
    mock_transform,
    mock_resolve_location,
    mock_save_raw,
    mock_save_records,
    mock_start_run,
    mock_finish_run,
):
    connection = MagicMock()

    locations = [
        {"city": "Bad City", "country_code": "US"},
        {"city": "New York", "country_code": "US"},
    ]

    mock_start_run.return_value = 1

    mock_geocode.side_effect = [
        RuntimeError("geocoding failed"),
        {"lat": 40.7128, "lon": -74.0060},
    ]

    raw_response = {"list": [{"dt": 1234567890}]}
    mock_fetch.return_value = raw_response

    records = [{"city": "New York", "aqi": 2}]
    mock_transform.return_value = records
    mock_resolve_location.return_value = 10

    result = run_pipeline(
        connection,
        locations,
        start=100,
        end=200,
    )

    assert result["status"] == "failed"
    assert result["records_processed"] == 1
    assert result["errors"] == ["Bad City: geocoding failed"]

    assert mock_geocode.call_count == 2
    mock_fetch.assert_called_once_with(
        40.7128,
        -74.0060,
        100,
        200,
    )
    mock_save_records.assert_called_once_with(
        connection,
        10,
        records,
    )
    mock_finish_run.assert_called_once_with(
        connection,
        1,
        "failed",
        records_processed=1,
        error_message="Bad City: geocoding failed",
    )