import csv
from pathlib import Path


def read_locations(file_path):
  file_path = Path(file_path)

  with file_path.open("r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)
    return list(reader)