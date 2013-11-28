from __future__ import print_function
from flask.ext.script import Command
from model.models import AirNowForecastArea, AirNowMonitoringSite, AirNowHourly, AirNowReportingArea, Area, Site
from geoalchemy2 import Geometry, Geography
import sqlalchemy.orm
from sqlalchemy.exc import IntegrityError

class ParseCommand(Command):
    tmpdir = '/tmp'
    cache_days = 1

    def run(self):

        from db import Session
        session = Session()

        # Special filename for most recent file
        if self.filename == 'recent':
            self.filename = self.recent()

        lines = self.get_lines()
        attrs = self.attributes()

        try:
            for line in lines:
                vals = line.strip().split('|')
                kvals = dict(zip(attrs, vals))

                model_inst = self.model()
                for col, val in kvals.items():
                    val = self.cleanval(col, val)
                    setattr(model_inst, col, val)
                
                #if hasattr(model_inst, 'country_code') and model_inst.country_code == 'CA':
                #    print('s', end='')
                #    continue

                try:
                    session.merge(model_inst)
                    session.commit()
                    print('.', end='')
                except Exception as inst:
                    session.rollback()
                    print('x', end='')
                    raise inst

        except Exception as inst:
            session.close()
            raise inst

        session.close()
        print('\nDone')


    def attributes(self):
        return [prop.key for prop in sqlalchemy.orm.class_mapper(self.model).iterate_properties
                if isinstance(prop, sqlalchemy.orm.ColumnProperty)]

    def get_lines(self):

        import datetime
        import os

        filepath = '{0}/{1}'.format(self.tmpdir, self.filename)

        if not os.path.isfile(filepath):
            print('Downloading file')
            self.download_file()
        else:
            today = datetime.datetime.today()
            modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            duration = today - modified_date
            if duration.days > self.cache_days:
                print('Downloading file')
                self.download_file()

        content = []
        with open(filepath) as f:
            for line in f:
                content.append(line.decode('cp850').encode('utf-8')) #(line.decode('cp850')) # iso-8859-1')) #.encode('utf-8'))
            #content = f.readlines()

        return content

    def download_file(self):
        ftp = self.ftp()
        ftp.cwd(self.ftp_dir)

        filepath = '{0}/{1}'.format(self.tmpdir, self.filename)
        ftp.retrbinary('RETR {0}'.format(self.filename), open(filepath, 'wb').write)
        ftp.quit()
        
        # convert using iconv
        #iconv -f iso-8859-1 -t utf8 /tmp/monitoring_site_locations.dat.orig > /tmp/monitoring_site_locations.dat

    def ftp(self):

        from ftplib import FTP
        import AcConfiguration
        c = AcConfiguration.AcConfiguration()
        ftp_user = c.settings['airnow']['username']
        ftp_pass = c.settings['airnow']['password']

        ftp = FTP('ftp.airnowapi.org', ftp_user, ftp_pass)
        return ftp

    def recent(self):

        ftp = self.ftp()
        files = ftp.nlst(self.ftp_dir)
        ftp.quit()
        
        files = [f for f in files if f[-4:] == '.dat']

        files.sort()
        return files.pop()

    def cleanval(self, col, val):

        if col == 'valid_time' and val == '':
            return '00:00:00'

        # mm/dd/yy
        import re
        m = re.match(r'([0-9]{2})/([0-9]{2})/([0-9]{2})', val)
        if m is not None:
            val = '20{0}'.format('-'.join([m.group(3), m.group(1), m.group(2)]))
        return val if len(val) > 0 else None
        

class ForecastAreas(ParseCommand):
    " Parse air now forecast areas - actual areas"
    ftp_dir = 'Locations'
    filename = 'reporting_area_locations_v2.dat'
    model = AirNowForecastArea

class MonitoringSites(ParseCommand):
    " Parse air now monitoring sites "
    ftp_dir = 'Locations'
    filename = 'monitoring_site_locations.dat'
    model = AirNowMonitoringSite

class Hourly(ParseCommand):
    " Parse air now hourly data "
    ftp_dir = 'HourlyData'
    filename = 'recent'
    model = AirNowHourly

class ReportingAreas(ParseCommand):
    " Parse air now reporting areas - individual reports "
    ftp_dir = 'ReportingArea'
    filename = 'reportingarea.dat'
    model = AirNowReportingArea

class LoadAreas(Command):

    def run(self):

        from db import Session
        session = Session()

        an_areas = session.query(AirNowForecastArea)
        for a in an_areas:

            area = Area()
            area.name = a.reporting_area
            area.country_iso = a.country_code
            area.state_province = a.state_code
            txt = 'POINT({} {})'.format(a.longitude, a.latitude)
            area.location = Geometry('Point').bind_expression(txt)

            try:
                session.merge(area)
                session.commit()
                print('.', end='')
            except IntegrityError as inst:
                session.rollback()
                print('-', end='')
            except Exception as inst:
                session.rollback()
                print('x', end='')
                raise inst


         
        #from db import engine
        #engine.execute("""
        #    INSERT INTO area (name, country_iso, state_province, location)
        #    SELECT reporting_area, country_code, state_code, ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')')
        #    FROM air_now_forecast_area
        #""")

class LoadAreaData(Command):

    def run(self):
        
        pass

class LoadSites(Command):

    def run(self):
        """ Load air now monitoring sites into site table """
        from db import Session
        session = Session()

        an_sites = session.query(AirNowMonitoringSite)
        for s in an_sites:

            site = Site()
            site.name = s.site_name
            site.country_iso = s.country_code
            site.state_province = s.state_code
            site.code = s.aqsid
            site.area_source_id = 1
            txt = 'POINT({} {})'.format(s.longitude, s.latitude)
            site.location = Geography('Point').bind_expression(txt)

            try:
                session.merge(site)
                session.commit()
                print('.', end='')
            except IntegrityError as inst:
                session.rollback()
                print('-', end='')
            except Exception as inst:
                session.rollback()
                print('x', end='')
                raise inst
