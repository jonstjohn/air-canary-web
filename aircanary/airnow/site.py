from bs4 import BeautifulSoup

national_url = 'http://www.airnow.gov/index.cfm?action=airnow.national_summary'
city_url = 'http://www.airnow.gov/index.cfm?action=airnow.local_city&cityid='
national_tmp = '/tmp/national.html'

def parse():
    """ Parse airnow national page for city ids and AQIs """
    import redis
    import re

    download_national()
    fh = open(national_tmp, 'r')
    soup = BeautifulSoup(fh)

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    pipe = r.pipeline()

    rows = soup.find('table').find_next_sibling().find_all('tr')
    pipe.delete('anc-ids')
    for row in rows:
       
        # Handle state block
        state_a = row.find('a', class_='stateblock')
        if state_a:
            state_abbr = state_a['name']
            print(state_abbr)

        # Main enclosing city table
        if row.find('table', class_='TblInvisibleFixed'):
            city_links = row.find_all('a', class_='NtnlSummaryCity')
            for link in city_links:
                href = link['href']
                city_id = None
                m = re.search('cityid=([0-9]*)', href)
                if m:
                    city_id = m.group(1)
                city = link.text

                tds = row.find('a', href=href).find_parent('td').find_next_siblings()
                
                current = tds[2].find('td').text.strip()
                k = 'anc-{}'.format(city_id)
                pipe.rpush('anc-ids', city_id)
                pipe.hmset(k, {'name': city, 'state': state_abbr, 'current': current})
                print('  {} ({}) {}, {}'.format(current, city_id, city, state_abbr))

    pipe.execute()
            
def download_national():
    """ Download national file """
    import os.path, time
    import urllib

    expire_time = 3600
    if not os.path.isfile(national_tmp) or os.path.getmtime(national_tmp) < time.time() - expire_time:
        print('Downloading file')
        urllib.urlretrieve (national_url, national_tmp)
    else:
        print('Skipping download')

if __name__ == '__main__':
    parse()
