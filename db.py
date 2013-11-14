from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import AcConfiguration

c = AcConfiguration.AcConfiguration()
username = c.settings['database']['username']
password = c.settings['database']['password']
host = c.settings['database']['host']
database = c.settings['database']['database']
dbtype = c.settings['database']['type']

engine = create_engine("{}://{}:{}@{}/{}".format(dbtype, username, password, host, database))

Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = Session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models.models
    Base.metadata.create_all(bind=engine)
