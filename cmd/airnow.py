from __future__ import print_function
from flask.ext.script import Command
from model.models import AirNowForecastArea, AirNowMonitoringSite, AirNowHourly, AirNowReportingArea, Area, Site, SiteData
from geoalchemy2 import Geometry, Geography
import sqlalchemy.orm
from sqlalchemy.exc import IntegrityError

from db import acdb

class ParseCommand(Command):
    tmpdir = '/tmp'
    cache_days = 1

    def run(self):

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
                    acdb.session.merge(model_inst)
                    acdb.session.commit()
                    print('.', end='')
                except Exception as inst:
                    acdb.session.rollback()
                    print('x', end='')
                    raise inst

        except Exception as inst:
            acdb.session.close()
            raise inst

        acdb.session.close()
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

        import os

        # Connect and change directory
        ftp = self.ftp()
        ftp.cwd(self.ftp_dir)

        # Check for local directory, create recursively if it doesn't exist
        local_dir = os.path.join(self.tmpdir, self.local_dir)
        if not os.path.exists(local_dir):
            os.mkdirs(local_dir)

        # Download file and write
        filepath = os.path.join(local_dir, self.filename)
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
    ftp_dir = 'location'
    local_dir = 'areas'
    filename = 'reporting_area_locations_v2.dat'
    model = AirNowForecastArea

class MonitoringSites(ParseCommand):
    " Parse air now monitoring sites "
    ftp_dir = 'Locations'
    local_dir = 'location'
    filename = 'monitoring_site_locations.dat'
    model = AirNowMonitoringSite

class Hourly(ParseCommand):
    " Parse air now hourly data "
    ftp_dir = 'HourlyData'
    local_dir = 'site_data'
    filename = 'recent'
    model = AirNowHourly

class ReportingAreas(ParseCommand):
    " Parse air now reporting areas - individual reports "
    ftp_dir = 'ReportingArea'
    local_dir = 'area_data'
    filename = 'reportingarea.dat'
    model = AirNowReportingArea

class LoadAreas(Command):

    def run(self):

        an_areas = acdb.session.query(AirNowForecastArea)
        for a in an_areas:

            area = Area()
            area.name = a.reporting_area
            area.country_iso = a.country_code
            area.state_province = a.state_code
            txt = 'POINT({} {})'.format(a.longitude, a.latitude)
            area.location = Geometry('Point').bind_expression(txt)

            try:
                acdb.session.merge(area)
                acdb.session.commit()
                print('.', end='')
            except IntegrityError as inst:
                acdb.session.rollback()
                print('-', end='')
            except Exception as inst:
                acdb.session.rollback()
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
        an_sites = acdb.session.query(AirNowMonitoringSite)
        for s in an_sites:

            site = Site()
            site.name = s.site_name
            site.country_iso = s.country_code
            site.state_province = s.state_name
            site.code = s.aqsid
            site.area_source_id = 1
            txt = 'POINT({} {})'.format(s.longitude, s.latitude)
            site.location = Geography('Point').bind_expression(txt)

            try:
                acdb.session.merge(site)
                acdb.session.commit()
                print('.', end='')
            except IntegrityError as inst:
                acdb.session.rollback()
                print('-', end='')
            except Exception as inst:
                acdb.session.rollback()
                print('x', end='')
                raise inst

class LoadHourly(Command):
    """ Load hourly data """
    col_map = {
        'BARPR': None, # barometric pressure, millibar
        'BC': None, # ??, ug/m3
        'CO': 'co', # Carbon monoxide, ppm
        'EC': None, # ?? ug/m3
        'NO': None, # ??, ppb
        'NO2': 'no2', # Nitrogen dioxide, ppb
        'NO2Y': None, # ??, ppb
        'NOX': 'nox', # nitrogen oxide, ppb
        'NOY': None, # ??, ppb
        'OZONE': 'ozone', # ozone, ppb
        'PM10': None, # particulate matter, 10 microns, ug/m3
        'PM2.5': 'pm25', # particulate matter, 2.5 microns, ug/m3
        'PRECIP': None, # precip, mm
        'RHUM': 'relative_humidity',  # relative humidity, percent
        'SO2': None, # sulfur dioxide, ppb
        'SRAD': None, # ??, watts/m2
        'TEMP': 'temperature', # temperature, celsius
        'WD': 'wind_direction', # wind direction, degrees
        'WS': 'wind_speed' # wind speed, m/s
    }

    def run(self):
        """ Load hourly data """
        from datetime import datetime, timedelta
        from math import ceil

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        q = acdb.session.query(AirNowHourly).filter(AirNowHourly.valid_date >= yesterday)
        count = q.count()

        batch_size = 1000

        iterations = int(ceil(count/1000))

        print(count)
        print(iterations)

        for i in range(0, iterations + 1):
            print("Processing {} - {} of {}".format(batch_size * i, batch_size * i + batch_size, count))
            self.process_hourly_batch(batch_size, batch_size * i)

    def process_hourly_batch(self, limit, offset):

        from datetime import datetime, timedelta

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        hourlies = acdb.session.query(AirNowHourly).filter(AirNowHourly.valid_date >= yesterday).limit(limit).offset(offset)
        for hourly in hourlies:

            # Check for parameter
            if not hourly.parameter in self.col_map:
                continue

            col = self.col_map[hourly.parameter]

            if not col:
                #print("Skipping " + hourly.parameter)
                continue

            # Create observed using valid_date, valid_time and gmt_offset
            observed = self.observed(hourly.valid_date, hourly.valid_time, hourly.gmt_offset)

            # Lookup site_id using aqsid
            site = self.site_from_aqsid(hourly.aqsid)

            # Check to see if this site data row already exists using site_id and observed
            try:
                site_data = acdb.session.query(SiteData).filter(SiteData.observed == observed, SiteData.site_id == site.site_id).one()
                print('f', end='')
            except sqlalchemy.orm.exc.NoResultFound:
                # If it does not exist, create a row for it
                print('c', end='')
                site_data = SiteData()
                site_data.observed = observed
                site_data.site_id = site.site_id

            value = float(hourly.value)

            # Convert ozone from ppb to ppm
            if col == 'ozone':
                value = value/1000

            # Set property
            try:
                setattr(site_data, col, hourly.value)

                acdb.session.add(site_data)
                acdb.session.commit()
                print('.', end='')
            except Exception as inst:
                acdb.session.rollback()
                print(inst)

    def observed(self, valid_date, valid_time, gmt_offset):
        """ Get observed from valid date/time and offset """
        # Construct date/time and convert to UTC using gmt_offset
        return str(valid_date) + ' ' + str(valid_time)

    def site_from_aqsid(self, aqsid):
        """ Get site id from aqsid """
        site = acdb.session.query(Site).filter(Site.code == aqsid and Site.area_source_id == 1).one()
        return site
