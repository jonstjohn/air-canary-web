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
from db import Session

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

    return render_template('ng/index.html')

@app.route('/ng/home')
def ng_home():

    return render_template('ng/home.html')

@app.route('/ng/site')
def ng_site():

    return render_template('ng/site.html')

@app.route('/ng/api')
def ng_api():
    return render_template('ng/api.html')

@app.route('/ng/about')
def ng_about():
    return render_template('ng/about.html')

@app.route('/ng/contact')
def ng_contact():
    return render_template('ng/contact.html')

@app.route('/site')
def sites():

    return render_template('sites.html', sites = Site.all_sites())

@app.route('/site/<code>')
def site(code):

   site = Site.from_code(code)

   return render_template('site.html', site = site, sites = Site.all_sites())

@app.route('/forecast/<code>', subdomain='api')
@app.route('/api/forecast/<code>')
def api_forecast(code):

    site = Site.from_code(code)
    response_data = site.forecast_data()
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.route('/site/<code>', defaults={'samples': 1}, subdomain='api')
@app.route('/site/<code>/<int:samples>', subdomain='api')
@app.route('/api/site/<code>', defaults={'samples': 1})
@app.route('/api/site/<code>/<int:samples>')
def api(code, samples):

    if code == 'all':
        response_data = Site.data_all(samples)
    else:
        site = Site.from_code(code)
        response_data = {'code': site.code, 'name': site.name, 'data': site.data(samples), 'forecast': site.forecast_data()}
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.route('/site', subdomain='api')
@app.route('/api/site')
def api_site():

    sites = Site.all_sites()
    response_data = []
    for site in sites:
        response_data.append({'code': site.code, 'name': site.name})
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()

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
