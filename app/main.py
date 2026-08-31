from fastapi import FastAPI

from .database import create_db_and_tables
from .routes import router


app = FastAPI(
    title="Environmental Sensor Data Ingestion Service",
    description=(
        "A lightweight API for receiving and storing "
        "environmental sensor readings."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Environmental Sensor Data Ingestion Service",
        "status": "running",
    }
