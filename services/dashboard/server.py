import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from services.dashboard.data import (
    get_available_locations,
    get_location_observations,
)

logger = logging.getLogger(__name__)

def _create_database_engine() -> Engine:
  load_dotenv()
  database_url = os.getenv("DATABASE_URL")

  if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

  return create_engine(database_url)


def create_app(engine: Engine | None = None) -> Flask:
  app = Flask(__name__)
  database_engine = (
    engine if engine is not None else _create_database_engine()
  )

  @app.errorhandler(SQLAlchemyError)
  def handle_database_error(error: SQLAlchemyError):
    logger.exception("Dashboard database operation failed")
    return jsonify({
      "error": {
        "code": "database_error",
        "message": "Unable to load dashboard data",
      }
    }), 500

  @app.get("/api/locations")
  def locations():
    with database_engine.connect() as connection:
      response = get_available_locations(connection)
    return jsonify(response)

  @app.get("/api/locations/<int:location_id>/observations")
  def location_observations(location_id: int):
    with database_engine.connect() as connection:
      response = get_location_observations(connection, location_id)

    if response is None:
      return jsonify({
        "error": {
          "code": "location_not_found",
          "message": "Location not found",
        }
      }), 404

    return jsonify(response)

  return app


def main() -> None:
  app = create_app()
  app.run()


if __name__ == "__main__":
  main()
