import xml.etree.ElementTree as et
import urllib2
import time

import sys
import os
sys.path.append('{0}/..'.format(os.path.dirname(os.path.abspath(__file__))))

import db
from model.models import Site, Data

session = db.session()
sites = session.query(Site).all()

for site in sites:

    print("Retrieving data for '{0}'".format(site.name))
    url = 'http://www.airquality.utah.gov/aqp/xmlFeed.php?id={0}'.format(site.code)

    # Get XML string
    f = urllib2.urlopen(url)
    xml_str = f.read()

    # Parse using etree
    tree = et.fromstring(xml_str)

    dates = []
    data = {}

    # Loop over each data tag
    for data_el in tree.iter('data'):

        date_el = data_el.find('date')
        date = date_el.text
        dates.append(date)
        data[date] = {}

        # Loop over each child element
        for child in data_el:
            if child.tag != 'date':
                data[date][child.tag] = child.text

    cols = ('ozone', 'ozone_8hr_avg', 'pm25', 'pm25_24hr_avg', 'nox',
        'no2', 'temperature', 'relative_humidity', 'wind_speed',
        'wind_direction', 'co', 'solar_radiation')

    for date, values in data.items():
        dp = Data()
        dp.site_id = site.site_id
        dp.observed = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date, '%m/%d/%Y %H:%M:%S'))
        for col, val in values.items():
            if col in cols:
                setattr(dp, col, val)
        session.merge(dp)
        session.commit()

session.close()

print('Done')
