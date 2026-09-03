import argparse
from datetime import datetime, timezone
from pipeline.extract.location_input import read_city_records
from pipeline.orchestration.runner import run_pipeline

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--start", required=True)
  parser.add_argument("--end", required=True)

  args = parser.parse_args()

  load_dotenv()
  database_url = os.getenv("DATABASE_URL")

  if not database_url:
      raise RuntimeError("DATABASE_URL is not set")

  engine = create_engine(database_url)

  start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
  end = datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)

  start_timestamp = int(start.timestamp())
  end_timestamp = int(end.timestamp())

  locations = read_city_records()

  print("Start:", start)
  print("End:", end)
  print("Start timestamp:", start_timestamp)
  print("End timestamp:", end_timestamp)
  print("Locations:", locations)

  with engine.connect() as connection:
    print("Database connection successful")

    result = run_pipeline(
      connection,
      locations, 
      start_timestamp,
      end_timestamp,
    )
    print("Status:", result["status"])
    print("Records processed:", result["records_processed"])

    if result["errors"]:
      print("Errors:")
      for error in result["errors"]:
        print("-", error)    

if __name__ == "__main__":
  main()