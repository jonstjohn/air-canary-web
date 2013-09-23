import xml.etree.ElementTree as et
import urllib2
import time
import feedparser

import sys
import os
import re

sys.path.append('{0}/..'.format(os.path.dirname(os.path.abspath(__file__))))

import db
from db import Session
from model.models import Site, Data, Forecast

session = Session()

try:
    sites = session.query(Site).all()

    title_date_regex = re.compile(r'(\d+)\/(\d+)\/(\d+)')
    description_regex = re.compile(r'Color: (.*) Condition: (.*)')

    for site in sites:

        print("Retrieving data for '{0}'".format(site.name))
        url = 'http://www.airquality.utah.gov/aqp/rssFeed.php?id={0}'.format(site.code)

        d = feedparser.parse(url)

        for entry in d.entries:
            forecast_date_match = title_date_regex.search(entry.title)
            description_match = description_regex.search(entry.description)
            
            if forecast_date_match and description_match:

                forecast_date =  "{0}-{1}-{2}".format(forecast_date_match.group(3), forecast_date_match.group(1), forecast_date_match.group(2))
                color = description_match.group(1).strip()
                condition = description_match.group(2).strip()

                print('  Adding forecast {0}'.format(forecast_date))
                published_date = "{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(
                    entry.published_parsed[0], entry.published_parsed[1],
                    entry.published_parsed[2], entry.published_parsed[3],
                    entry.published_parsed[4], entry.published_parsed[5]
                )

                if color and condition:

                    f = Forecast()
                    f.site_id = site.site_id
                    f.forecast_date = forecast_date
                    f.color = color
                    f.description = condition
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
