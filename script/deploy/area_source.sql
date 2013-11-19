CREATE TABLE area_source (
    area_source_id serial primary key,
    name varchar(100)
);

CREATE TABLE area_code (
    area_id INT,
    code VARCHAR(20),
    CONSTRAINT pkey PRIMARY KEY (area_id, code),
    CONSTRAINT areaSourceCode_areaId FOREIGN KEY (area_id)
        REFERENCES area (area_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
