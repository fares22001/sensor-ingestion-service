from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from .database import get_session
from .models import SensorReading
from .schemas import SensorReadingCreate, SensorReadingResponse


router = APIRouter(prefix="/readings", tags=["Sensor Readings"])


@router.post(
    "",
    response_model=SensorReadingResponse,
    status_code=201,
)
def create_reading(
    reading_data: SensorReadingCreate,
    session: Session = Depends(get_session),
):
    reading = SensorReading(
        sensor_id=reading_data.sensor_id,
        timestamp=reading_data.timestamp,
        reading=reading_data.reading,
    )

    try:
        session.add(reading)
        session.commit()
        session.refresh(reading)

        return reading
    
    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="A reading already exists for this sensor and timestamp.",
        )

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to store sensor reading.",
        )


@router.get(
    "",
    response_model=list[SensorReadingResponse],
)
def get_readings(
    sensor_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    statement = select(SensorReading)

    if sensor_id:
        statement = statement.where(
            SensorReading.sensor_id == sensor_id
        )

    statement = statement.order_by(
        SensorReading.timestamp.desc()
    ).limit(limit)

    return session.exec(statement).all()


@router.get(
    "/{reading_id}",
    response_model=SensorReadingResponse,
)
def get_reading(
    reading_id: int,
    session: Session = Depends(get_session),
):
    reading = session.get(SensorReading, reading_id)

    if not reading:
        raise HTTPException(
            status_code=404,
            detail="Sensor reading not found.",
        )

    return reading
