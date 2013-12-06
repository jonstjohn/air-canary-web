from flask.ext.sqlalchemy import SQLAlchemy
import AcConfiguration

c = AcConfiguration.AcConfiguration()
username = c.settings['database']['username']
password = c.settings['database']['password']
host = c.settings['database']['host']
database = c.settings['database']['database']
dbtype = c.settings['database']['type']

db_uri = "{}://{}:{}@{}/{}".format(dbtype, username, password, host, database)
acdb = None

def init(app):
    # Initialize db
    global acdb
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    acdb = SQLAlchemy(app)
    return acdb
