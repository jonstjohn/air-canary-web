from flask.ext.script import Command

class Current(Command):
    "prints hello world"

    def run(self):
        print "hello world"

class ParseData(Command):
    "Downloads and parses primary data"

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
        import datetime
        import db
        from db import Session
        from model.models import Site, Data

        session = Session()
        sites = session.query(Site).all()

        try:
            for site in sites:

                print("Retrieving data for '{0}'".format(site.name))
                xml_str = self.url2xml('http://www.airquality.utah.gov/aqp/xmlFeed.php?id={0}'.format(site.code))
                data = self.xml2data(xml_str)

                cols = ('ozone', 'ozone_8hr_avg', 'pm25', 'pm25_24hr_avg', 'nox',
                    'no2', 'temperature', 'relative_humidity', 'wind_speed',
                    'wind_direction', 'co', 'solar_radiation')

                for date, values in data.items():
                    dp = Data()
                    dp.site_id = site.site_id
                    observed_raw =  datetime.datetime.strptime(date, '%m/%d/%Y %H:%M:%S')
                    adjusted_raw = observed_raw + datetime.timedelta(hours=2)

                    dp.observed = datetime.datetime.strftime(adjusted_raw, '%Y-%m-%d %H:%M:%S')
                    for col, val in values.items():
                        if col in cols:
                            setattr(dp, col, val)
                    try:
                        session.merge(dp)
                        session.commit()
                    except:
                        session.rollback()
                        raise

        except:
            session.close()
            raise

        session.close()
        print('Done')
