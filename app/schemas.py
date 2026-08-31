from datetime import datetime

from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):
    sensor_id: str = Field(min_length=1)
    timestamp: datetime
    reading: float


class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: str
    timestamp: datetime
    reading: float