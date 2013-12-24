CREATE TABLE IF NOT EXISTS grib_ozone (
    cell integer,
    val integer,
    primary key (cell)
);

CREATE TABLE IF NOT EXISTS grib_pm25 (
    cell integer,
    val integer,
    primary key (cell)
);

CREATE TABLE IF NOT EXISTS grib_today (
    cell integer,
    val integer,
    primary key (cell)
);

CREATE TABLE IF NOT EXISTS grib_tomorrow (
    cell integer,
    val integer,
    primary key (cell)
);

CREATE TABLE IF NOT EXISTS grib_multi (
    cell integer,
    start timestamp not null,
    ozone integer,
    pm25 integer,
    today integer,
    tomorrow integer,
    primary key (cell, start)
);
