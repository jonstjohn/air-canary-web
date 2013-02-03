from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base();
from sqlalchemy import Column, Integer, String, VARCHAR, Text, Date, DATETIME, DECIMAL, CHAR, Integer, ForeignKey
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
        return session.query(Site).order_by(Site.name)

    @staticmethod
    def from_code(code):
        """
        Get site from code
        """
        session = db.session()
        return session.query(Site).filter(Site.code == code).one()

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
            'ozone': str(self.ozone),
            'ozone_8hr_avg': str(self.ozone_8hr_avg),
            'pm25': str(self.pm25),
            'pm25_24hr_avg': str(self.pm25_24hr_avg),
            'nox': str(self.nox),
            'no2': str(self.no2),
            'temperature': str(self.temperature),
            'relative_humidity': str(self.relative_humidity),
            'wind_speed': str(self.wind_speed),
            'wind_direction': str(self.wind_direction),
            'co': str(self.co),
            'solar_radiation': str(self.solar_radiation)
        }
