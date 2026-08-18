""" location input tests
Branch SCRUM-20
Subtask SCRUM-25
Local path: services/pipeline/tests/extract/test_location_input.py

Check path:

    $env:PYTHONPATH = 'services/pipeline/src'
    python -c "from pipeline.extract.location_validation import validate_city_records; print(validate_city_records([]))"

Check valid:

    $env:PYTHONPATH = 'services/pipeline/src'
    python -c "from pipeline.extract.location_validation import validate_city_records; records=[{'city':'Charlotte','country_code':'US','state':'NC'}]; print(validate_city_records(records))"

"""

import pytest
from pipeline.extract.location_validation import validate_city_records

def test_valid_record():
    records = [{'city': 'Charlotte', 'country_code': 'US', 'state': 'NC'}]
    valid, errors = validate_city_records(records)
    assert len(valid) == 1
    assert len(errors) == 0

def test_missing_city():
    records = [{'city': '', 'country_code': 'US', 'state': ''}]
    valid, errors = validate_city_records(records)
    assert len(valid) == 0
    assert errors[0].message == 'Missing required field: city'

def test_missing_country_code():
    records = [{'city': 'Paris', 'country_code': '', 'state': ''}]
    valid, errors = validate_city_records(records)
    assert len(valid) == 0
    assert errors[0].message == 'Missing required field: country_code'

def test_invalid_country_code():
    records = [{'city': 'LA', 'country_code': 'USA', 'state': ''}]
    valid, errors = validate_city_records(records)
    assert len(valid) == 0
    assert 'Invalid country_code' in errors[0].message

