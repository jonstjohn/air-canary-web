from flask import Flask
from flask import render_template
from flask import request, session
from flask import abort, redirect, url_for, flash, jsonify, Response
import json
import AcConfiguration

from functools import wraps
from model.models import Site, Data

#import sqlalchemy
#import json
import db

app = Flask(__name__)

# set the secret key.  keep this really secret:
c = AcConfiguration.AcConfiguration()
app.secret_key = c.settings['flask']['secret_key']
#app.debug = True if c.settings['configuration']['debug'] == 1 else False
app.debug = True

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/api/<code>', defaults={'samples': 1})
@app.route('/api/<code>/<int:samples>')
def api(code, samples):

    site = Site.from_code(code)
    site_data = site.data(samples)
    response = Response(json.dumps(site_data), status=200, mimetype='application/json')
    response.cache_control.no_cache = True
    return response

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)

ADMINS = ['jonstjohn@gmail.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'jonstjohn@gmail.com',
                               ADMINS, 'Air Canary Error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
