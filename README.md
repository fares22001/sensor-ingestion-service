# Environmental Sensor Data Ingestion Service

A lightweight FastAPI service for receiving environmental sensor readings and storing them in a database. The focus here was on building something simple and reliable — an entry point for sensor data that's easy to understand, test, and extend, rather than something over-engineered for the scope of the exercise.

Each reading is made up of three fields:

- `sensor_id` — the ID of the sensor sending the reading
- `timestamp` — when the reading was taken, in ISO 8601 format
- `reading` — the measurement itself, as a floating-point number

SQLite is used for storage. It's lightweight, requires no separate setup, and is more than sufficient for the scope of this project.

## Tech Stack

- Python 3.10+
- FastAPI
- SQLModel
- Pydantic
- SQLite
- Pytest
- Uvicorn

## Project Structure

```
sensor-ingestion-service/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── schemas.py
├── tests/
│   └── test_readings.py
├── .gitignore
├── README.md
└── requirements.txt
```

- **main.py** — creates the FastAPI app and registers the routes
- **database.py** — sets up the database connection and provides sessions
- **models.py** — defines the database table and its constraints
- **schemas.py** — validates the data coming into the API
- **routes.py** — the API endpoints and the logic behind them
- **test_readings.py** — automated tests for the API

## Getting Started

**Requirements:** Python 3.10 or later.

Clone the repo and set up a virtual environment:

```bash
git clone <repository-url>
cd sensor-ingestion-service
python -m venv .venv
```

Activate it (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies and run the app:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive Swagger docs at `http://127.0.0.1:8000/docs` — a convenient way to try out the endpoints without a separate API client.

## API

### Create a Reading

`POST /readings`

Accepts a sensor reading and stores it.

```json
{
  "sensor_id": "sensor_001",
  "timestamp": "2026-08-31T12:00:00Z",
  "reading": 25.4
}
```

Returns `201 Created` along with the stored reading:

```json
{
  "id": 1,
  "sensor_id": "sensor_001",
  "timestamp": "2026-08-31T12:00:00Z",
  "reading": 25.4
}
```

### Get All Readings

`GET /readings`

Returns all stored readings. Filter by sensor with the `sensor_id` query parameter:

```
GET /readings?sensor_id=sensor_001
```

### Get a Reading by ID

`GET /readings/{reading_id}`

```
GET /readings/1
```

Returns `404 Not Found` if the reading doesn't exist.

## Validation and Error Handling

Every request is validated before anything touches the database:

- `sensor_id` must be present and non-empty
- `timestamp` must be a valid ISO 8601 datetime
- `reading` must be a valid number

Database errors are handled gracefully, with failed transactions rolled back to avoid leaving partial writes behind.

**Duplicate readings:** a unique constraint on `sensor_id` + `timestamp` prevents the same sensor from storing two readings at the same moment. Submitting a duplicate returns `409 Conflict`, which protects against accidentally storing the same measurement twice.

## Database Design

A single table, `sensor_readings`:

| Column    | Type     | Description                   |
| --------- | -------- | ----------------------------- |
| id        | Integer  | Primary key                   |
| sensor_id | String   | Identifier of the sensor      |
| timestamp | DateTime | Time the reading was recorded |
| reading   | Float    | Sensor measurement            |

`sensor_id` and `timestamp` are indexed to keep filtering and time-based queries efficient, and the same unique constraint on `sensor_id` + `timestamp` applies at the database level.

SQLite is a fine choice here — it avoids the overhead of running a separate database server for what this assignment needs.

## Running the Tests

```bash
python -m pytest
```

The tests cover the core behavior: successful reading creation, input validation, duplicate protection, retrieving stored readings, and handling missing ones.

## Assumptions

- Each sensor is identified by a unique `sensor_id`.
- A sensor won't send more than one reading for the same timestamp.
- Timestamps come from the sensor/source already in ISO 8601 format.
- `reading` is left as a generic measurement, since the assignment doesn't specify a unit.
- SQLite is sufficient for this scope — no need for anything heavier.
- Authentication and authorization are out of scope.
- The service trusts that the external source provides a valid sensor ID.
- This is a simple ingestion service, not intended to include message processing or analytics.

## Scaling This Further

The current setup — a single FastAPI instance with SQLite — works well for the scope of this assignment, but it wouldn't hold up under real load. If this service had to support 10,000 sensors each sending a reading every second, that's roughly:

- 10,000 readings/second
- 600,000 readings/minute
- 36 million readings/hour
- 864 million readings/day

At that volume, a single instance writing directly to SQLite becomes the bottleneck fast. Here's how I'd approach scaling it, by separating ingestion, processing, and storage into independent layers.

**1. Scale the FastAPI layer.** Since the app is stateless, it can run as multiple instances behind a load balancer, and more instances can be added as traffic grows.

**2. Introduce a message broker.** Rather than every request hitting the database directly, FastAPI would validate the reading and publish it to something like Apache Kafka. Separate worker processes would then consume from Kafka and write to the database. This decouples ingestion from storage — if the database temporarily can't keep up, messages simply queue in Kafka until the consumers catch up, and multiple consumers can process in parallel.

**3. Replace SQLite with a database built for this.** Something like PostgreSQL with TimescaleDB, or another time-series-oriented database, with indexing on `sensor_id` and `timestamp`, time-based partitioning, sensible retention policies, and replication for availability. The exact choice would depend on expected query patterns and operational needs.

                         Sensors
                            |
                            v
                     Load Balancer
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          FastAPI        FastAPI        FastAPI
             |              |              |
             +--------------+--------------+
                            |
                            v
                          Kafka
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          Worker         Worker         Worker
             |              |              |
             +--------------+--------------+
                            |
                            v
                  Scalable Database

**4. Add data retention and aggregation.** At 864 million readings a day, keeping every raw reading forever isn't realistic. I'd keep recent raw data for detailed analysis, aggregate older data into hourly or daily statistics, and archive or drop data past a defined retention window.

**5. Add monitoring and reliability.** At production scale, I'd want visibility into API request rates, failed requests, Kafka consumer lag, database performance, processing latency, and general application health — so bottlenecks and failures get caught before they cascade.

The overall goal is to make each layer — API, message processing, and database — scale independently, so the system isn't tied to a single FastAPI instance and a local SQLite file the way this assignment's implementation currently is.
