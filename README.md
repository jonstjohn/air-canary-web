air-canary-web
==============

[Air Canary website](http://www.aircanary.com)

Air quality reports for Utah and beyond!


Install Node, Bower, Bootstrap
=============================
sudo apt-get update
sudo apt-get install nodejs
sudo apt-get install -y python-software-properties python g++ make
sudo add-apt-repository -y ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
sudo npm install -g bower
bower install bootstrap


Crons
=============================

Utah air quality from DEQ:
/home/jonstjohn/ac/air-canary-web/manage.py utah_current
/home/jonstjohn/ac/air-canary-web/manage.py utah_forecast

AirNow:
/home/jonstjohn/ac/air-canary-web/manage.py airnow_hourly
/home/jonstjohn/ac/air-canary-web/manage.py airnow_reporting_areas
/home/jonstjohn/ac/air-canary-web/manage.py airnow_grib
/home/jonstjohn/ac/air-canary-web/manage.py airnow_load_hourly
