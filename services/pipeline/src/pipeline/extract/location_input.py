"""Read city records from the configured CSV file.
branch SCRUM-20
Subtask SCRUM-23 read configured location input
local path: services\pipeline\src\pipeline\extract\location_input.py

Check logging:

    $env:PYTHONPATH = "services/pipeline/src" 
    python -c "import logging; logging.basicConfig(level=logging.INFO); from pipeline.extract.location_input import read_city_records; read_city_records()"

Check csv:

    $env:PYTHONPATH = "services/pipeline/src" 
    python -c "from pipeline.extract.location_input import read_city_records; print(read_city_records())"

"""

import csv
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DEFAULT_CITIES_CSV = Path('services/pipeline/config/cities.csv')

def _get_cities_csv_path() -> Path:
    logger.info(f'function get_cities_csv_path was invoked')
    raw = os.getenv('CITIES_CSV_FILE')
    path = Path(raw) if raw else DEFAULT_CITIES_CSV
    logger.debug('Cities CSV path resolved: %s', path)
    return path

def read_city_records(csv_path: Path | str | None = None) -> list[dict[str, str]]:
    logger.debug("read_city_records called with csv_path=%r", csv_path)
    
    path = Path(csv_path) if csv_path is not None else _get_cities_csv_path()
    logger.info('Reading cities CSV: %s', path)

    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            logger.info('Cities CSV is empty (no header): %s', path)
            return []

        rows: list[dict[str, str]] = []
        for row in reader:
            normalized = {k: (v or '') for k, v in row.items()}
            rows.append(normalized)

    return rows