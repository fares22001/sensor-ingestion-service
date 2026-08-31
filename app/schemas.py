from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SensorReadingCreate(BaseModel):

    sensor_id: str = Field(min_length=1)

    timestamp: datetime

    reading: float

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value):
        if not isinstance(value, str):
            raise ValueError("timestamp must be a valid ISO 8601 datetime")

        try:
            # ISO 8601 uses "Z" for UTC, while fromisoformat()
            # expects "+00:00" in some Python versions.
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be a valid ISO 8601 datetime")

        return value


class SensorReadingResponse(BaseModel):

    id: int

    sensor_id: str

    timestamp: datetime

    reading: float