from __future__ import print_function
from flask.ext.script import Command

class Current(Command):
    "Downloads and parses current data"

    debug = False

    def url2xml(self, url):
        """ Get XML from URL """
        import urllib2
        f = urllib2.urlopen(url)
        xml_str = f.read()
        return xml_str

    def xml2data(self, xml_str):
        """ Convert XML to data dict """
        import xml.etree.ElementTree as et

        tree = et.fromstring(xml_str)

        data = {}

        # Loop over each data tag
        for data_el in tree.iter('data'):

            date_el = data_el.find('date')
            date = date_el.text
            data[date] = {}

            # Loop over each child element
            for child in data_el:
                if child.tag != 'date':
                    data[date][child.tag] = child.text

        return data

    def run(self):
        """ Run command """
        from datetime import datetime, timedelta
        from pytz import timezone
        import pytz
        import db
        from db import Session
        from model.models import Area, AreaData

        if self.debug:
            import logging
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        session = Session()
        areas = session.query(Area).filter(Area.area_source_id == 2).all()

        mst = timezone('MST')

        try:
            # Loop over each area
            for area in areas:

                # Get XML and convert to data
                print("\nRetrieving data for '{0}'".format(area.name))
                xml_str = self.url2xml('http://www.airquality.utah.gov/aqp/xmlFeed.php?id={0}'.format(area.code))
                data = self.xml2data(xml_str)

                cols = ('ozone', 'ozone_8hr_avg', 'pm25', 'pm25_24hr_avg', 'nox',
                    'no2', 'temperature', 'relative_humidity', 'wind_speed',
                    'wind_direction', 'co', 'solar_radiation')

                for date, values in data.items():

                    dp = AreaData()
                    dp.area_id = area.area_id

                    # Adjust datetime by 1 hour according to DEQ
                    dt =  datetime.strptime(date, '%m/%d/%Y %H:%M:%S') + timedelta(hours=1)

                    # Convert to MST, which is what the observed datetime is always in, regardless of DST
                    dt_mst = mst.localize(dt)

                    # Convert to UTC for storage
                    dt_utc = dt_mst.astimezone(pytz.utc)

                    # Format UTC date/time for storage
                    dp.observed = datetime.strftime(dt_utc, '%Y-%m-%d %H:%M:%S')

                    for col, val in values.items():
                        if col in cols:
                            if val and val[0] != '-':
                                setattr(dp, col, val)
                    try:
                        session.merge(dp)
                        session.commit()
                        print('.', end='')
                    except:
                        session.rollback()
                        print('x', end='')
                        raise

        except:
            session.close()
            raise

        session.close()
        print('\nDone')

class Forecast(Command):
    " Downloads and parses daily forecast "

    def run(self):

        import feedparser

        import re

        import db
        from db import Session
        from model.models import Area, AreaForecast

        session = Session()

        colormap = {'Good': 'green', 'Moderate': 'yellow'}

        try:
            areas = session.query(Area).filter(Area.area_source_id == 2).all()

            title_date_regex = re.compile(r'(\d+)\/(\d+)\/(\d+)')
            description_regex = re.compile(r'Health: (.*) Action: (.*)')

            for area in areas:

                print("Retrieving data for '{0}'".format(area.name))
                url = 'http://www.airquality.utah.gov/aqp/rssFeed.php?id={0}'.format(area.code)

                d = feedparser.parse(url)
                for entry in d.entries:
                    forecast_date_match = title_date_regex.search(entry.title)
                    description_match = description_regex.search(entry.description)

                    if forecast_date_match and description_match:

                        forecast_date =  "{0}-{1}-{2}".format(forecast_date_match.group(3), forecast_date_match.group(1), forecast_date_match.group(2))
                        health = description_match.group(1).strip()
                        color = colormap[health]

                        action = description_match.group(2).strip()

                        print('  Adding forecast {0}'.format(forecast_date))
                        published_date = "{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                            entry.published_parsed[0], entry.published_parsed[1],
                            entry.published_parsed[2], entry.published_parsed[3],
                            entry.published_parsed[4], entry.published_parsed[5]
                        )

                        if color and health:

                            f = AreaForecast()
                            f.area_id = area.area_id
                            f.forecast_date = forecast_date
                            f.color = color
                            f.description = health
                            f.published = published_date

                            try:
                                session.merge(f)
                                session.commit()
                            except:
                                session.rollback()
                                raise

        except:
            session.close()
            raise

        session.close()

        print('Done')


