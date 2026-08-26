from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

from sqlalchemy import CheckConstraint, String, BigInteger, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class Location(Base):
    __tablename__="locations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("city", "country_code", "latitude", "longitude"),
        CheckConstraint("length(country_code) = 2"),
        CheckConstraint("latitude >= -90 AND latitude <= 90"),
        CheckConstraint("longitude >= -180 AND longitude <= 180"),
    ) 


from sqlalchemy import DateTime, ForeignKey, SmallInteger, UniqueConstraint, Integer, text
from sqlalchemy.dialects.postgresql import JSONB

class AirQualityRecord(Base):
    __tablename__ = "air_quality_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    aqi: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    pm2_5: Mapped[float | None] = mapped_column(Float, nullable=True) 
    pm10: Mapped[float | None] = mapped_column(Float, nullable=True) 
    no2: Mapped[float | None] = mapped_column(Float, nullable=True) 
    o3: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("location_id", "observed_at"),
        CheckConstraint("aqi >= 1 AND aqi <= 5")
    ) 


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('running', 'success', 'failed')"),
        CheckConstraint("records_processed >= 0"),
    )

class RawApiResponse(Base):
    __tablename__ = "raw_api_responses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
