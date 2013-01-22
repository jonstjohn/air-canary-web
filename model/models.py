from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base();
from sqlalchemy import Column, Integer, String, VARCHAR, Text, Date, DATETIME, DECIMAL, CHAR, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Table

class Site(Base):

    __tablename__ = 'site'

    site_id = Column(Integer, primary_key = True)
    code = Column(VARCHAR(10))
    name = Column(VARCHAR(50))
    country_iso = Column(CHAR(3))
    state_province = Column(VARCHAR(5))

    data = relationship("Data", uselist = False, backref = "site")

class Data(Base):

    __tablename__ = 'data'

    site_id = Column(Integer, ForeignKey('site.site_id'), primary_key = True)
    observed = Column(DATETIME, primary_key = True, nullable = False)
    ozone = Column(DECIMAL(10,3))
    ozone_8hr_avg = Column(DECIMAL(10, 3))
    pm25 = Column(DECIMAL(6, 2))
    pm25_24hr_avg = Column(DECIMAL(6, 2))
    nox = Column(DECIMAL(10, 3))
    no2 = Column(DECIMAL(10, 3))
    temperature = Column(DECIMAL(5,2))
    relative_humidity = Column(DECIMAL(5,2))
    wind_speed = Column(DECIMAL(5,2))
    wind_direction = Column(Integer)
    co = Column(DECIMAL(5,2))
    solar_radiation = Column(Integer)

