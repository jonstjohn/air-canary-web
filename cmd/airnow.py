from __future__ import print_function
from flask.ext.script import Command
from model.models import AirNowForecastArea, AirNowMonitoringSite, AirNowHourly, AirNowReportingArea
import sqlalchemy.orm

class ParseCommand(Command):
    " Download and process forecast areas from AirNow "

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
                    val = self.cleanval(val)
                    setattr(model_inst, col, val)
                
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
            content = f.readlines()

        return content

    def download_file(self):
        ftp = self.ftp()
        ftp.cwd(self.ftp_dir)
        ftp.retrbinary('RETR {0}'.format(self.filename), open('{0}/{1}'.format(self.tmpdir, self.filename), 'wb').write)
        ftp.quit()

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

    def cleanval(self, val):

        import re

        # mm/dd/yy
        m = re.match(r'([0-9]{2})/([0-9]{2})/([0-9]{2})', val)
        if m is not None:
            val = '20{0}'.format('-'.join([m.group(3), m.group(1), m.group(2)]))
        return val
        

class ForecastAreas(ParseCommand):

    ftp_dir = 'Locations'
    filename = 'reporting_area_locations_v2.dat'
    model = AirNowForecastArea

class MonitoringSites(ParseCommand):

    ftp_dir = 'Locations'
    filename = 'monitoring_site_locations.dat'
    model = AirNowMonitoringSite

class Hourly(ParseCommand):

    ftp_dir = 'HourlyData'
    filename = 'recent'
    model = AirNowHourly

class ReportingAreas(ParseCommand):

    ftp_dir = 'ReportingArea'
    filename = 'reportingarea.dat'
    model = AirNowReportingArea
