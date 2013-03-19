from flask import Flask
from flask import render_template
from flask import request, session
from flask import abort, redirect, url_for, flash, jsonify, Response
import json
import AcConfiguration

from functools import wraps
from model.models import Site, Data

from raven.contrib.flask import Sentry

#import sqlalchemy
#import json
import db

app = Flask(__name__)

# Sentry config
app.config['SENTRY_DSN'] = 'https://c4e3385afab54c018041e7a577a75374:966792c8e18a441f9429731b65c0f853@app.getsentry.com/6569'
sentry = Sentry(app)

# set the secret key.  keep this really secret:
c = AcConfiguration.AcConfiguration()
app.secret_key = c.settings['flask']['secret_key']
#app.debug = True if c.settings['configuration']['debug'] == 1 else False
app.debug = True

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/api/forecast/<code>')
def api_forecast(code):

    site = Site.from_code(code)
    response_data = site.forecast_data()
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.route('/api/<code>', defaults={'samples': 1})
@app.route('/api/<code>/<int:samples>')
def api(code, samples):

    if code == 'all':
        response_data = Site.data_all(samples)
    else:
        site = Site.from_code(code)
        response_data = {'code': site.code, 'name': site.name, 'data': site.data(samples)}
    print(response_data)
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
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
