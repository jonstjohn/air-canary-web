CREATE TABLE IF NOT EXISTS forecast (
    site_id INT UNSIGNED NOT NULL,
    forecast_date DATE NOT NULL,
    color VARCHAR(12) NOT NULL,
    description varchar(100) NOT NULL,
    published DATETIME NOT NULL,
    PRIMARY KEY (site_id, forecast_date),
    INDEX (forecast_date),
    CONSTRAINT fk_siteForecast_site_siteId
        FOREIGN KEY (site_id)
        REFERENCES site (site_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = INNODB;
