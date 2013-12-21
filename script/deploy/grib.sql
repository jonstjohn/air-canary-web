CREATE TABLE IF NOT EXISTS grib_data (
    start timestamp not null,
    latitude decimal(6, 2) not null,
    longitude decimal(6, 3) not null,
    location geography(POINT, 4326) not null,
    ozone integer,
    pm25 integer,
    combined integer,
    forecast_today integer,
    forecast_tomorrow integer
);

CREATE INDEX gribData_location_index ON grib_data (location);
