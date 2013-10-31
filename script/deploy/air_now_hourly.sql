CREATE TABLE air_canary.air_now_hourly(
    valid_date date not null,
    valid_time time not null,
    aqsid char(9) not null,
    site_name varchar(20),
    gmt_offset tinyint(1),
    parameter varchar(10) not null,
    units varchar(10),
    value varchar(6),
    data_source varchar(100),
    primary key (valid_date, valid_time, aqsid, parameter),
    index (aqsid),
    index (parameter)
) engine = innodb;
