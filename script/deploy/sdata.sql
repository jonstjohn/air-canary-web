CREATE TABLE IF NOT EXISTS site_data (
    site_id int not null,
    observed timestamp,
    ozone decimal(10, 3),
    ozone_8hr_avg decimal(10, 3),
    pm25 decimal(6,2),
    pm25_24hr_avg decimal(6,2),
    nox decimal(10,3),
    no2 decimal(10,3),
    temperature decimal(5,2),
    relative_humidity decimal(5,2),
    wind_speed decimal(5,2),
    wind_direction smallint,
    co decimal(5,2),
    solar_radiation int,
    PRIMARY KEY (site_id, observed),
    CONSTRAINT site
        FOREIGN KEY (site_id)
        REFERENCES site (site_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX siteData_observed_index ON site_data (observed);
