CREATE TABLE IF NOT EXISTS site (
    site_id int unsigned primary key auto_increment,
    code varchar(10) not null,
    name varchar(50) not null,
    country_iso char(3) not null,
    state_province varchar(5),
    INDEX (name),
    INDEX (code),
    INDEX (country_iso, state_province)
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS data (
    site_id int unsigned not null,
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
    PRIMARY KEY (site_id, observed),
    INDEX (observed),
    CONSTRAINT site
        FOREIGN KEY (site_id)
        REFERENCES site (site_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = INNODB;

INSERT INTO site (code, name, country_iso, state_province) VALUES
('boxelder', 'Box Elder', 'USA', 'UT'),
('cache', 'Cache', 'USA', 'UT'),
('rs', 'Duchesne', 'USA', 'UT'),
('p2', 'Price', 'USA', 'UT'),
('slc', 'SLC/Davis', 'USA', 'UT'),
('tooele', 'Tooele', 'USA', 'UT'),
('vl', 'Uintah', 'USA', 'UT'),
('washington', 'Washington', 'USA', 'UT'),
('weber', 'Weber', 'USA', 'UT');
