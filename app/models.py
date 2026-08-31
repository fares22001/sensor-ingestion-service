from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class SensorReading(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "sensor_id",
            "timestamp",
            name="uq_sensor_timestamp",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    sensor_id: str = Field(index=True)

    timestamp: datetime = Field(index=True)

    reading: float
