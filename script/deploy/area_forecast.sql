CREATE TABLE IF NOT EXISTS area_forecast (
    area_id INT NOT NULL,
    forecast_date DATE NOT NULL,
    color VARCHAR(12) NOT NULL,
    description varchar(100) NOT NULL,
    published TIMESTAMP NOT NULL,
    PRIMARY KEY (area_id, forecast_date),
    CONSTRAINT fk_areaForecast_area_areaId
        FOREIGN KEY (area_id)
        REFERENCES area (area_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX areaForecast_forecastDate ON area_forecast (forecast_date);
