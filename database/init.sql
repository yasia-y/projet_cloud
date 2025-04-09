-- SQL script to initialize the PostgreSQL database.
-- Should define the sensor_data table with appropriate columns (e.g., id, timestamp, sensor_id, value, alert).
-- Include types, constraints, and indexes if needed.

CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    plant_id TEXT NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
