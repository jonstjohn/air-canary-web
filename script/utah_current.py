import time
from datetime import date
import re

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

session = db.session()

try:
    sites = session.query(Site).all()

    # Wind dirs
    wind_dirs = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}

    # Regex for stripping non-numeric
    non_numeric = re.compile(r'[^\d.]+')

    # Regex for wind
    wind_regex = re.compile(r'([A-Z]*)\s*([\d.]*) mph')

    current_year = date.today().year
    for site in sites:

        code = site.code if site.code != 'washington' else 'wash'

        url = 'http://www.airquality.utah.gov/aqp/{0}-currentconditions.html'.format(code)
        print("Retrieving data for '{0}' {1}".format(site.name, url))
        soup = _get_soup_from_url(url)
        date_str = soup.find('span', "style51").contents[1]
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        for comment in comments:
            if str(comment) == 'DECurrentDateTime':
                observed_str = comment.next_sibling.string.strip()
                observed = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime("{0} {1}".format(current_year, observed_str), '%Y %A %B %d, %I:%M %p'))
            elif str(comment) == 'DEPM25Value':
                pm25 = non_numeric.sub('', comment.next_sibling.string.strip())
            elif str(comment) == 'DEOzoneValue':
                ozone = non_numeric.sub('', comment.next_sibling.string.strip())
            elif str(comment) == 'DETempValue':
                temp = non_numeric.sub('', comment.next_sibling.string.strip())
            elif str(comment) == 'DEWindValue':
                wind = comment.next_sibling.string.strip()
                wind_match = wind_regex.search(wind)
                wind_dir_str = wind_match.group(1).strip()
                wind_dir = wind_dirs[wind_dir_str]
                wind_speed = wind_match.group(2).strip()
        print('Date: {0}'.format(observed))
        print('PM 2.5: {0}'.format(pm25))
        print('Ozone: {0}'.format(ozone))
        print('Temp: {0}'.format(temp))
        print('Wind: {0} - {1} - {2}'.format(wind, wind_dir, wind_speed))

        dp = Data()
        dp.site_id = site.site_id
        dp.observed = observed
        
        if is_number(pm25):
            dp.pm25 = pm25
        if is_number(ozone):
            dp.ozone = ozone
        if is_number(temp):
            dp.temperature = temp
        if is_number(wind_speed):
            dp.wind_speed = wind_speed
        if is_number(wind_dir):
            dp.wind_direction = wind_dir
        session.merge(dp)
        session.commit()

except:
    session.close()
    raise

session.close()

print('Done')
