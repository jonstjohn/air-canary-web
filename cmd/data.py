from __future__ import print_function
from flask.ext.script import Command

class ParseData(Command):
    "Downloads and parses primary data"

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
        from model.models import Site, Data

        if self.debug:
            import logging
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

        sites = acdb.session.query(Site).all()

        mst = timezone('MST')

        try:
            # Loop over each site
            for site in sites:

                # Get XML and convert to data
                print("\nRetrieving data for '{0}'".format(site.name))
                xml_str = self.url2xml('http://www.airquality.utah.gov/aqp/xmlFeed.php?id={0}'.format(site.code))
                data = self.xml2data(xml_str)

                cols = ('ozone', 'ozone_8hr_avg', 'pm25', 'pm25_24hr_avg', 'nox',
                    'no2', 'temperature', 'relative_humidity', 'wind_speed',
                    'wind_direction', 'co', 'solar_radiation')

                for date, values in data.items():

                    dp = Data()
                    dp.site_id = site.site_id

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
                        acdb.session.merge(dp)
                        acdb.session.commit()
                        print('.', end='')
                    except:
                        acdb.session.rollback()
                        print('x', end='')
                        raise

        except:
            acdb.session.close()
            raise

        acdb.session.close()
        print('\nDone')

class ParseForecast(Command):
    " Downloads and parses daily forecast "

    def run(self):

        import feedparser

        import re

        import db
        from model.models import Site, Data, Forecast

        colormap = {'Good': 'green', 'Moderate': 'yellow'}

        try:
            sites = acdb.session.query(Site).all()

            title_date_regex = re.compile(r'(\d+)\/(\d+)\/(\d+)')
            description_regex = re.compile(r'Health: (.*) Action: (.*)')

            for site in sites:

                print("Retrieving data for '{0}'".format(site.name))
                url = 'http://www.airquality.utah.gov/aqp/rssFeed.php?id={0}'.format(site.code)

                d = feedparser.parse(url)
                print(d.entries);
                for entry in d.entries:
                    forecast_date_match = title_date_regex.search(entry.title)
                    description_match = description_regex.search(entry.description)

                    if forecast_date_match and description_match:

                        forecast_date =  "{0}-{1}-{2}".format(forecast_date_match.group(3), forecast_date_match.group(1), forecast_date_match.group(2))
                        health = description_match.group(1).strip()
                        color = colormap[health]

                        action = description_match.group(2).strip()

                        print('  Adding forecast {0}'.format(forecast_date))
                        print(entry.published_parsed)
                        published_date = "{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                            entry.published_parsed[0], entry.published_parsed[1],
                            entry.published_parsed[2], entry.published_parsed[3],
                            entry.published_parsed[4], entry.published_parsed[5]
                        )




                        if color and health:

                            f = Forecast()
                            f.site_id = site.site_id
                            f.forecast_date = forecast_date
                            f.color = color
                            f.description = health
                            f.published = published_date

                            try:
                                acdb.session.merge(f)
                                acdb.session.commit()
                            except:
                                acdb.session.rollback()
                                raise

        except:
            acdb.session.close()
            raise

        acdb.session.close()

        print('Done')


