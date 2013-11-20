from flask import Flask
from flask.ext.script import Manager
from cmd.data import ParseData, ParseForecast
from cmd.utah.data import Current, Forecast
from cmd.airnow import ForecastAreas, MonitoringSites, Hourly, ReportingAreas, LoadAreas

app = Flask(__name__)
# configure your app

manager = Manager(app)

manager.add_command('parse_data', ParseData())
manager.add_command('parse_forecast', ParseForecast())
manager.add_command('airnow_forecast_areas', ForecastAreas())
manager.add_command('airnow_monitoring_sites', MonitoringSites())
manager.add_command('airnow_hourly', Hourly())
manager.add_command('airnow_reporting_areas', ReportingAreas())
manager.add_command('airnow_load_areas', LoadAreas())

manager.add_command('utah_current', Current())
manager.add_command('utah_forecast', Forecast())

if __name__ == "__main__":
    manager.run()
