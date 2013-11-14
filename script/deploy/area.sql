CREATE TABLE IF NOT EXISTS area (
    area_id int unsigned primary key auto_increment,
    name varchar(50) not null,
    country_iso char(3) not null,
    state_province varchar(5),
    latitude decimal(10,8) not null,
    longitude decimal(11,8) not null,
    INDEX (name),
    UNIQUE INDEX (country_iso, state_province, name),
    INDEX (latitude, longitude)
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS area_data (
    area_id int unsigned not null,
    observed datetime,
    ozone decimal(10, 3) unsigned,
    ozone_8hr_avg decimal(10, 3) unsigned,
    pm25 decimal(6,2) unsigned,
    pm25_24hr_avg decimal(6,2) unsigned,
    nox decimal(10,3) unsigned,
    no2 decimal(10,3) unsigned,
    temperature decimal(5,2),
    relative_humidity decimal(5,2) unsigned,
    wind_speed decimal(5,2) unsigned,
    wind_direction smallint unsigned,
    co decimal(5,2) unsigned,
    solar_radiation int unsigned,
    PRIMARY KEY (area_id, observed),
    INDEX (observed),
    CONSTRAINT area
        FOREIGN KEY (area_id)
        REFERENCES area (area_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = INNODB;
/*
INSERT INTO site (code, name, country_iso, state_province) VALUES
('boxelder', 'Box Elder', 'USA', 'UT'),
('cache', 'Cache', 'USA', 'UT'),
('rs', 'Duchesne', 'USA', 'UT'),
('p2', 'Price', 'USA', 'UT'),
('slc', 'SLC/Davis', 'USA', 'UT'),
('tooele', 'Tooele', 'USA', 'UT'),
('vl', 'Uintah', 'USA', 'UT'),
('washington', 'Washington', 'USA', 'UT'),
('weber', 'Weber', 'USA', 'UT'),
( 'utah', 'Utah', 'USA', 'UT');
*/

INSERT INTO air_canary.area (name, country_iso, state_province, latitude, longitude) SELECT reporting_area, country_code, state_code, latitude, longitude FROM air_canary.air_now_forecast_area;

