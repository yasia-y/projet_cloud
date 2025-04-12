CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    sensor_version VARCHAR(10) NOT NULL,
    plant_id INTEGER NOT NULL,  -- Changé en INTEGER
    temperature FLOAT NOT NULL, -- Ajouté
    humidity FLOAT NOT NULL,    -- Ajouté
    timestamp TIMESTAMPTZ NOT NULL,
    anomaly BOOLEAN DEFAULT FALSE,
    cross_sensor_issue BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_plant ON sensor_data (plant_id);
CREATE INDEX idx_timestamp ON sensor_data (timestamp);
