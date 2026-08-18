"""Validate location input
Branch SCRUM-20
Subtask SCRUM-24
Local path: services/pipeline/src/pipeline/extract/location_validation.py

Check valid:

    $env:PYTHONPATH = "services/pipeline/src" 
    python -c "from pipeline.extract.location_input import read_city_records; from pipeline.extract.location_validation import validate_city_records; v,e = validate_city_records(read_city_records()); print('valid=', v); print('errors=', e)"

Check errors:

    $env:PYTHONPATH = "services/pipeline/src" 
    python -c "from pipeline.extract.location_validation import validate_city_records; records=[{'city':'', 'country_code':'US','state':''},{'city':'Paris','country_code':'','state':''},{'city':'LA','country_code':'USA','state':''}]; v,e=validate_city_records(records); print('valid=', v); print('errors=', [err.message for err in e])"

Checking logging:

    $env:PYTHONPATH = "services/pipeline/src" 
    python -c "import logging; logging.basicConfig(level=logging.DEBUG); from pipeline.extract.location_input import read_city_records; from pipeline.extract.location_validation import validate_city_records; validate_city_records(read_city_records())"

"""

import re
from dataclasses import dataclass
from typing import Any
import logging

logger = logging.getLogger(__name__)

COUNTRY_CODE_RE = re.compile(r'^[A-Z]{2}$')

@dataclass(frozen=True)
class LocationValidationError:
    row_number: int
    message: str
    row: dict[str, Any]

def validate_city_records(
    records: list[dict[str, str]],) -> tuple[list[dict[str, str]], list[LocationValidationError]]:
    valid: list[dict[str, str]] = []
    errors: list[LocationValidationError] = []
    logger.info(f'function validate_city_records was invoked')

    for row_number, row in enumerate(records, start=2):
        city = (row.get('city') or '').strip()
        country_code = (row.get('country_code') or '').strip().upper()
        state = (row.get('state') or '').strip()

        if not city and not country_code and not state:
            continue

        if not city:
            errors.append(LocationValidationError(row_number, 'Missing required field: city', row))
            continue

        if not country_code:
            errors.append(LocationValidationError(row_number, 'Missing required field: country_code', row))
            continue

        if not COUNTRY_CODE_RE.fullmatch(country_code):
            errors.append(
                LocationValidationError(
                    row_number,
                    "Invalid country_code (expected ISO-2 like 'US')",
                    row,
                )
            )
            continue

        valid.append({'city': city, 'country_code': country_code, 'state': state})

    logger.debug('Validated %d records -> %d valid, %d errors', len(records), len(valid), len(errors))

    return valid, errors