import time

import sys
import os
sys.path.append('{0}/..'.format(os.path.dirname(os.path.abspath(__file__))))

import db
from bs4 import BeautifulSoup, Comment

from model.models import Site, Data

# Get soup from URL
def _get_soup_from_url(url):

    import urllib2, httplib
    httplib.HTTPConnection.debuglevel = 1
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 3.5.30729; InfoPath.2; .NET CLR 3.0.30729)')
    opener = urllib2.build_opener()
    return BeautifulSoup(opener.open(request).read())

session = db.session()
sites = session.query(Site).all()

for site in sites:

    url = 'http://www.airquality.utah.gov/aqp/{0}-currentconditions.html'.format(site.code)
    print("Retrieving data for '{0}' {1}".format(site.name, url))
    soup = _get_soup_from_url(url)
    date_str = soup.find('span', "style51").contents[1]
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        if str(comment) == 'DECurrentDateTime':
            date_str = comment.next_sibling.string.strip()
        elif str(comment) == 'DEPM25Value':
            pm25 = comment.next_sibling.string.strip()
        elif str(comment) == 'DEOzoneValue':
            ozone = comment.next_sibling.string.strip()
        elif str(comment) == 'DETempValue':
            temp = comment.next_sibling.string.strip()
    print('Date: {0}'.format(date_str))
    print('PM 2.5: {0}'.format(pm25))
    print('Ozone: {0}'.format(ozone))
    #print('Temp: {0}'.format(temp))
    #print(comments)
    break

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
