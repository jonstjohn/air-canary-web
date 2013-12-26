#DROP TABLE grib_ozone;
#DROP TABLE grib_pm25;
#DROP TABLE grib_today;
#DROP TABLE grib_tomorrow;
#DROP TABLE grib_multi;

CREATE TABLE IF NOT EXISTS grib_ozone (
    x integer,
    y integer,
    val integer,
    primary key (x, y)
);

CREATE TABLE IF NOT EXISTS grib_pm25 (
    x integer,
    y integer,
    val integer,
    primary key (x, y)
);

CREATE TABLE IF NOT EXISTS grib_today (
    x integer,
    y integer,
    val integer,
    primary key (x, y)
);

CREATE TABLE IF NOT EXISTS grib_tomorrow (
    x integer,
    y integer,
    val integer,
    primary key (x, y)
);

CREATE TABLE IF NOT EXISTS grib_multi (
    x integer,
    y integer,
    start timestamp not null,
    ozone integer,
    pm25 integer,
    today integer,
    tomorrow integer,
    primary key (x, y, start)
);
