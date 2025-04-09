-- Script de création des tables
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(50),
    temperature FLOAT,
    humidity FLOAT
);
