from db import Base
from db import Session
from sqlalchemy import Column, Integer, String, VARCHAR, Text, Date, DATETIME, DATE, DECIMAL, CHAR, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Table
import db

class Site(Base):

    __tablename__ = 'site'

    site_id = Column(Integer, primary_key = True)
    code = Column(VARCHAR(10))
    name = Column(VARCHAR(50))
    country_iso = Column(CHAR(3))
    state_province = Column(VARCHAR(5))

    data = relationship("Data", uselist = False, backref = "site")

    def data(self, samples):

        session = Session()
        data = session.query(Data).filter(Data.site_id == self.site_id).order_by(Data.observed.desc()).limit(samples).all()
        result = []
        for d in data:
            result.append(d.data())
        session.close()
        return result

    def forecast_data(self):
        session = Session()
        data = session.query(Forecast).filter(Forecast.site_id == self.site_id).order_by(Forecast.forecast_date.desc()).limit(3).all()
        result = []
        for d in data:
            result.append(d.data())
        result.reverse()
        session.close()
        return result

    @staticmethod
    def data_all(samples):

        sites = Site.all_sites()
        result = []
        for site in sites:
            result.append({'code': site.code, 'name': site.name, 'data': site.data(samples)})
        return result

    @staticmethod
    def all_sites():
        session = Session()
        sites = session.query(Site).order_by(Site.name)
        session.close()
        return sites

    @staticmethod
    def from_code(code):
        """
        Get site from code
        """
        session = Session()
        site = session.query(Site).filter(Site.code == code).one()
        session.close() 
        return site

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

    def data(self):

        # Convert datetime to mountain, which is local for all existing sites
        import pytz
        from pytz import timezone
        mountain = timezone('America/Denver')

        return {
            'observed': str(pytz.utc.localize(self.observed).astimezone(mountain).isoformat()),
            'ozone': float(self.ozone) if self.ozone else '',
            'ozone_8hr_avg': float(self.ozone_8hr_avg) if self.ozone_8hr_avg else '',
            'pm25': float(self.pm25) if self.pm25 else '',
            'pm25_24hr_avg': float(self.pm25_24hr_avg) if self.pm25_24hr_avg else '',
            'nox': float(self.nox) if self.nox else '',
            'no2': float(self.no2) if self.no2 else '',
            'temperature': float(self.temperature) if self.temperature else '',
            'relative_humidity': float(self.relative_humidity) if self.relative_humidity else '',
            'wind_speed': float(self.wind_speed) if self.wind_speed else '',
            'wind_direction': float(self.wind_direction) if self.wind_direction else '',
            'co': float(self.co) if self.co else '',
            'solar_radiation': float(self.solar_radiation) if self.solar_radiation else ''
        }

class Forecast(Base):

    __tablename__ = 'forecast'

    site_id = Column(Integer, primary_key = True, nullable = False)
    forecast_date = Column(DATE, primary_key = True, nullable = False)
    color = Column(VARCHAR(12), nullable = False)
    description = Column(VARCHAR(100), nullable = False)
    published = Column(DATETIME, nullable = False)

    def data(self):

        import pytz
        from pytz import timezone
        mountain = timezone('America/Denver')

        return {
            'date': str(self.forecast_date) + 'T08:00:00.000Z',
            'color': str(self.color) if self.color else '',
            'description': str(self.description) if self.description else '',
            'published': str(pytz.utc.localize(self.published).astimezone(mountain).isoformat())
        }

    @staticmethod
    def data_3day(site_id):

        pass

class AirNowForecastArea(Base):

    __tablename__ = 'air_now_forecast_area'

    reporting_area = Column(VARCHAR(45), primary_key = True, nullable = False)
    state_code = Column(CHAR(2), primary_key = True, nullable = False)
    country_code = Column(CHAR(2), primary_key = True, nullable = False)
    forecasts = Column(VARCHAR(3))
    action_day = Column(VARCHAR(50))
    latitude = Column(VARCHAR(9))
    longitude = Column(VARCHAR(11))
    gmt_offset = Column(Integer)
    daylight_savings = Column(VARCHAR(3))
    standard_time_label = Column(VARCHAR(3))
    daylight_time_label = Column(VARCHAR(3))
    twc_code = Column(VARCHAR(5))
    usa_today = Column(VARCHAR(3))
    forecast_source = Column(VARCHAR(100))

class AirNowMonitoringSite(Base):

    __tablename__ = 'air_now_monitoring_site'

    aqsid = Column(CHAR(9), primary_key = True, nullable = False) # id
    parameter = Column(VARCHAR(10), primary_key = True, nullable = False) # parameter, eg OZONE
    site_code = Column(CHAR(4)) # last 4 digits of aqsid
    site_name = Column(VARCHAR(20)) # site name
    status = Column(VARCHAR(8)) # operational status
    agency_id = Column(VARCHAR(4)) # 4-digit agency id assigned by AirNow
    agency_name = Column(VARCHAR(60)) # Agency name
    epa_region = Column(CHAR(2)) # EPA region
    latitude = Column(VARCHAR(9))
    longitude = Column(VARCHAR(11))
    elevation = Column(Integer)
    gmt_offset = Column(Integer)
    country_code = Column(CHAR(2)) # FIPS
    cmsa_code = Column(CHAR(4)) # 4 digit consolidate metro stat area FIPS
    cmsa_name = Column(VARCHAR(50))
    msa_code = Column(CHAR(4)) # FIPS metro stat area
    msa_name = Column(VARCHAR(50))
    state_code = Column(CHAR(2)) # two digit FIPS code
    state_name = Column(CHAR(2)) # Abbrev, e.g., UT
    county_code = Column(CHAR(9)) # Nine-digit GNIS Feature ID of the named populated place in which site is located.
    county_name = Column(VARCHAR(25))
    city_code = Column(CHAR(9)) # Nine-digit GNIS Feature ID of the named population place in which site is located
