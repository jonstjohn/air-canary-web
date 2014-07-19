test_files = ['US-13121204.grib2', 'US-13121204_combined.grib2', 'US-13121204_pm25.grib2', 'US-13121205.grib2', 'US-13121205_combined.grib2', 'US-13121205_pm25.grib2', 'US-13121206.grib2', 'US-13121206_combined.grib2', 'US-13121206_pm25.grib2', 'US-13121207.grib2', 'US-13121207_combined.grib2', 'US-13121207_pm25.grib2', 'US-13121208.grib2', 'US-13121208_combined.grib2', 'US-13121208_pm25.grib2', 'US-13121209.grib2', 'US-13121209_combined.grib2', 'US-13121209_pm25.grib2', 'US-13121210.grib2', 'US-13121210_combined.grib2', 'US-13121210_pm25.grib2', 'US-13121211.grib2', 'US-13121211_combined.grib2', 'US-13121211_pm25.grib2', 'US-13121212.grib2', 'US-13121212_combined.grib2', 'US-13121212_pm25.grib2', 'US-13121213.grib2', 'US-13121213_combined.grib2', 'US-13121213_pm25.grib2', 'US-13121214.grib2', 'US-13121214_combined.grib2', 'US-13121214_pm25.grib2', 'US-13121215.grib2', 'US-13121215_combined.grib2', 'US-13121215_pm25.grib2', 'US-13121216.grib2', 'US-13121216_combined.grib2', 'US-13121216_pm25.grib2', 'US-13121217.grib2', 'US-13121217_combined.grib2', 'US-13121217_pm25.grib2', 'US-13121218.grib2', 'US-13121218_combined.grib2', 'US-13121218_pm25.grib2', 'US-131213-ForecastTomorrow.grib2']

class Ftp:

    ftp = None
    def __init__(self):

        self.ftp = self.open()

    def download_file(self):

        import os

        # Connect and change directory
        ftp = self.ftp
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

    def grib2_recent(self):

        files = self.dir('GRIB2')
        #files = test_files

        sorted_files = {}
        for file in files:

            if 'grib2' not in file:
                continue

            k = self.key_from_file(file)
            if not k in sorted_files:
                sorted_files[k] = []
            sorted_files[k].append(file)

        for k, v in sorted_files.iteritems():
            sorted_files[k].sort()
            sorted_files[k] = sorted_files[k].pop()

        return sorted_files

    def grib2_download(self):

        import os
        import re
        from django.conf import settings
        grib2_dir = settings.AIRNOW_GRIB_DIR

        if not os.path.exists(grib2_dir):
            os.makedirs(grib2_dir)

        files = self.grib2_recent()
        self.ftp.cwd('GRIB2')
        for file in files.values():
            print(file)
            # Download file and write
            filepath = os.path.join(grib2_dir, re.sub(r'US-[0-9]+', 'US-current', file))
            self.ftp.retrbinary('RETR {0}'.format(file), open(filepath, 'wb').write)

    def key_from_file(self, file):

        import re
        pattern = re.compile('US-[0-9]*(.*).grib2')
        m = pattern.match(file)
        return m.group(1)

    def dir(self, dir=None):

        return self.ftp.nlst(dir)

    def open(self):

        from ftplib import FTP
        import os

        ftp_user = os.environ['AIRNOW_USERNAME']
        ftp_pass = os.environ['AIRNOW_PASSWORD']

        ftp = FTP('ftp.airnowapi.org', ftp_user, ftp_pass)
        return ftp

    def close(self):

        self.ftp.quit()

if __name__ == '__main__':

    f = Ftp()
    f.grib2_download()
    f.close()

