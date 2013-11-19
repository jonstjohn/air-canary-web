INSERT INTO area (name, country_iso, state_province, location, area_source_id)
VALUES
    ('Box Elder County', 'US', 'UT', ST_GeographyFromText('POINT(-113.1000 41.5100)'), 2),
    ('Cache County', 'US', 'UT', ST_GeographyFromText('POINT(-111.7500 41.6900)'), 2),
    ('Duchesne County', 'US', 'UT', ST_GeographyFromText('POINT(-110.45278 40.18972)'), 2),
    ('Salt Lake / Davis County', 'US', 'UT', ST_GeographyFromText('POINT(-111.8833 40.7500)'), 2),
    ('Tooele County', 'US', 'UT', ST_GeographyFromText('POINT(-113.1800 40.4500)'), 2),
    ('Uintah County', 'US', 'UT', ST_GeographyFromText('POINT(-109.5200 40.1300)'), 2),
    ('Utah County', 'US', 'UT', ST_GeographyFromText('POINT(-111.6608 40.2444)'), 2),
    ('Washington County', 'US', 'UT', ST_GeographyFromText('POINT(-113.5200 37.2800)'), 2),
    ('Weber County', 'US', 'UT', ST_GeographyFromText('POINT(-111.9200 41.3000)'), 2)
;
