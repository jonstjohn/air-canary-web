from flask import Flask
from flask.ext.script import Manager
from cmd.data import ParseData, ParseForecast
from cmd.airnow import ForecastAreas, MonitoringSites

app = Flask(__name__)
# configure your app

manager = Manager(app)

manager.add_command('parse_data', ParseData())
manager.add_command('parse_forecast', ParseForecast())
manager.add_command('airnow_forecast_areas', ForecastAreas())
manager.add_command('airnow_monitoring_sites', MonitoringSites())

if __name__ == "__main__":
    manager.run()
