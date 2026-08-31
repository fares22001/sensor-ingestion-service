from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_create_reading():
    response = client.post(
        "/readings",
        json={
            "sensor_id": "test_sensor",
            "timestamp": "2026-08-30T12:00:00Z",
            "reading": 25.5,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["sensor_id"] == "test_sensor"
    assert data["reading"] == 25.5


def test_invalid_reading():
    response = client.post(
        "/readings",
        json={
            "sensor_id": "",
            "timestamp": "not-a-date",
            "reading": "invalid",
        },
    )

    assert response.status_code == 422


def test_duplicate_reading():
    payload = {
        "sensor_id": "duplicate_sensor",
        "timestamp": "2026-08-31T13:00:00Z",
        "reading": 30.0,
    }

    first_response = client.post("/readings", json=payload)

    assert first_response.status_code == 201

    second_response = client.post("/readings", json=payload)

    assert second_response.status_code == 409
