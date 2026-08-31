# Environmental Sensor Data Ingestion Service

# Overview

This project is a lightweight FastAPI service built to receive environmental readings from sensors and store them in a database.

The main goal of the service is to provide a simple and reliable entry point for sensor data while keeping the application easy to understand and extend.

Each sensor reading contains:

- 'sensor_i' - The ID of the sensor sending the reading.
- 'timestamp' - The time the reading was taken, using ISO 8601 format.
- 'reading' - The actual sensor reading as a number.

For this assignment, I used SQLite as the database since it is lightweight and does not require any additional database setup.



## Tech Stack

- Python 3.10+
- FastAPI
- SQLModel
- Pydantic
- SQLite
- Pytest
- Uvicorn


## Project Structure

sensor-ingestion-service/
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── schemas.py
│
├── tests/
│   └── test_readings.py
│
├── .gitignore
├── README.md
└── requirements.txt


What each file does:

main.py: Creates the FastAPI application and registers the routes.
database.py: Handles the SQLite database connection and sessions.
models.py: Defines the database table used to store sensor readings.
schemas.py: Defines and validates the data received by the API.
routes.py: Contains the API endpoints and their logic.
test_readings.py: Contains tests for the API.

Getting Started

Requirements

Make sure you have Python 3.10 or later installed.

1. Clone the repository
git clone <repository-url>
cd sensor-ingestion-service

2. Create a virtual environment
python -m venv .venv

3. Activate the virtual environment
.venv\Scripts\Activate.ps1

4. Install the dependencies
pip install -r requirements.txt

5. Start the application
uvicorn app.main:app --reload

The API will then be available at:

http://127.0.0.1:8000

FastAPI also provides interactive API documentation, which can be opened at:

http://127.0.0.1:8000/docs

From there, the endpoints can be tested directly from the browser.




API:

1. Create a Reading

POST /readings

Example request:

{
    "sensor_id": "sensor_001",
    "timestamp": "2026-08-31T12:00:00Z",
    "reading": 25.4
}

A successful request returns 201 Created and the stored reading, including its generated ID.

2. Get All Readings

GET /readings

Returns the stored sensor readings.

3. Readings can also be filtered by sensor:

GET /readings?sensor_id=sensor_001

4. Get a Reading by ID

GET /readings/{reading_id}

Example:

GET /readings/1

If the requested reading does not exist, the API returns 404 Not Found.

5. Validation and Error Handling

The API validates incoming data before storing it.

For example:

sensor_id must not be empty.
timestamp must be a valid ISO 8601 datetime.
reading must be a number.

The service also handles database errors and rolls back failed transactions.

A reading with the same sensor_id and timestamp cannot be inserted twice. If this happens, the API returns:

409 Conflict

This prevents duplicate sensor readings from being stored accidentally.

6. Database Design

The application currently uses one table called sensor_readings.

Column	    Type	        Description
id	          Integer	     Primary key
sensor_id	 String	     Sensor identifier
timestamp	 DateTime	  Time of the reading
reading	    Float	     Sensor measurement

The sensor_id and timestamp fields are indexed to make common queries more efficient.

There is also a unique constraint on:

sensor_id + timestamp

This means that the same sensor cannot have two readings with the exact same timestamp.

SQLite is used for this assignment because it is lightweight and does not require a separate database server.

7. Running the Tests

The project includes automated tests using Pytest.

To run them:

python -m pytest

The tests cover the main API behavior, including successful requests, validation errors, and duplicate readings.

8. Assumptions

A few assumptions were made while building the service:

Each sensor has a unique sensor_id.
A sensor should not send more than one reading for the same timestamp.
The timestamp is provided by the sensor/source and is expected to use ISO 8601 format.
The reading field represents a generic environmental measurement. The assignment does not specify a particular unit.
SQLite is sufficient for the scope of this assignment.
Authentication and authorization are outside the scope of the exercise.
The service is expected to receive valid sensor IDs from the external sources.

9. Scalability

The current implementation is intentionally simple and uses one FastAPI application with SQLite.

This works well for a small number of sensors, but the architecture would need to change if the service had to support 10,000 sensors sending one reading every second.

That would mean approximately:

10,000 readings/second
600,000 readings/minute
36 million readings/hour
864 million readings/day

At that point, SQLite and a single FastAPI instance would not be a good fit.

I would scale the system in a few steps.

1. Multiple FastAPI Instances

The FastAPI application can be kept stateless and deployed as multiple instances behind a load balancer.

For example:

Sensors
   |
   v
Load Balancer
   |
   +---- FastAPI
   |
   +---- FastAPI
   |
   +---- FastAPI

This allows incoming requests to be distributed across multiple servers and makes it possible to add more instances when traffic increases.

2. Message Broker

Instead of having every API instance write directly to the database, I would introduce a message broker such as Apache Kafka.

The flow would become:

Sensors
   |
   v
Load Balancer
   |
   v
FastAPI
   |
   v
Kafka
   |
   v
Consumers
   |
   v
Database

FastAPI would validate the reading and publish it to Kafka. Separate consumer processes would then read the messages and store them in the database.

This would also provide a buffer if the database temporarily cannot keep up with the incoming traffic.

3. Scalable Database

SQLite would be replaced with a database better suited for large amounts of time-series data, such as PostgreSQL with TimescaleDB or another suitable time-series database.

The database could also use partitioning and appropriate indexes based on the sensor and timestamp to keep queries efficient as the amount of data grows.

4. Data Retention

Sensor data can grow very quickly at this scale.

A retention policy could be introduced so that recent raw readings are kept for a certain period, while older data is either removed or aggregated into hourly/daily statistics.

This would help control storage requirements.

Overall Approach

The main idea would be to make each part of the system independently scalable:

              Load Balancer
                    |
                    |         
       FastAPI   FastAPI   FastAPI
                    |         
                    |
                  Kafka
                    |
                    |         
       Worker    Worker    Worker
                    |         
                    |
             Scalable Database

This allows the API, message processing, and database layers to be scaled independently depending on where the bottleneck is.