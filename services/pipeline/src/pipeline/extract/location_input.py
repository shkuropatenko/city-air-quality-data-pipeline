import csv
import os
from pathlib import Path


DEFAULT_CITIES_CSV = Path("services/pipeline/config/cities.csv")


def _get_cities_csv_path() -> Path:
    raw = os.getenv("CITIES_CSV_FILE")
    return Path(raw) if raw else DEFAULT_CITIES_CSV


def read_locations(csv_path: Path | str | None = None) -> list[dict[str, str]]:
  path = Path(csv_path) if csv_path is not None else _get_cities_csv_path()

  with path.open("r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)

    if reader.fieldnames is None:
      return []

    rows = []

    for row in reader:
      normalized = {
        key: (value or "")
        for key, value in row.items()
      }

      rows.append(normalized)

  return rows