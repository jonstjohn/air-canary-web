from flask import Flask
from flask.ext.script import Manager
from cmd.data import ParseData

app = Flask(__name__)
# configure your app

manager = Manager(app)

manager.add_command('parse_data', ParseData())

if __name__ == "__main__":
    manager.run()
