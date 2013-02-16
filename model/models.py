from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base();
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

        session = db.session()
        data = session.query(Data).filter(Data.site_id == self.site_id).order_by(Data.observed.desc()).limit(samples).all()
        result = []
        for d in data:
            result.append(d.data())
        session.close()
        return result

    def forecast_data(self):
        session = db.session()
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
        session = db.session()
        sites = session.query(Site).order_by(Site.name)
        session.close()
        return sites

    @staticmethod
    def from_code(code):
        """
        Get site from code
        """
        session = db.session()
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

        return {
            'observed': str(self.observed),
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

        return {
            'date': str(self.forecast_date),
            'color': str(self.color) if self.color else '',
            'description': str(self.description) if self.description else '',
            'published': str(self.published)
        }

    @staticmethod
    def data_3day(site_id):

        pass

