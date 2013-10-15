from flask import Flask
from flask.ext.script import Manager
from cmd.data import Current, Forecast

app = Flask(__name__)
# configure your app

manager = Manager(app)

manager.add_command('current', Current())
manager.add_command('forecast', Forecast())

if __name__ == "__main__":
    manager.run()
