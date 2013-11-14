from flask import Flask
from flask import render_template
from flask import request, session
from flask import abort, redirect, url_for, flash, jsonify, Response
from flask import g
from werkzeug.contrib.cache import RedisCache
import json
import AcConfiguration

from functools import wraps
from model.models import Site, Data, Area

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

def generate_csrf_token():
    if '_csrf_token' not in session:
        import string
        import random
        session['_csrf_token'] = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(30)])
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def cache(timeout=300, key='view:{0}'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache = RedisCache()
            cache_key = 'view:{0}'.format(request.path)
            response = cache.get(cache_key)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(cache_key, response, timeout)
            return response
        return decorated_function
    return decorator

app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.route('/')
def index():
    """ Home page """
    return render_template('ng/index.html')

@app.route('/ng/<template>')
def ng_template(template):
    """ Render angular template """
    allowed_templates = ['home', 'site', 'api', 'about', 'contact']
    if template not in allowed_templates:
        abort(404)

    return render_template('ng/{0}.html'.format(template))

@app.route('/location/<latitude>/<longitude>')
def county(latitude, longitude):
    """ Get city/state/zip/code from latitude and longitude """
    import requests
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&sensor=false".format(latitude, longitude)
    resultStr = requests.get(url)
    results = resultStr.json()
    city = None
    county = None
    state = None
    zipcode = None
    for r in results['results']:
        for comp in r['address_components']:
            if 'administrative_area_level_2' in comp['types']:
                county = comp['long_name']
            elif 'administrative_area_level_1' in comp['types']:
                state = comp['long_name']
            elif 'locality' in comp['types']:
                city = comp['long_name']
            elif 'postal_code' in comp['types']:
                zipcode = comp['long_name']

    codes = {'Box Elder': 'boxelder', 'Cache': 'cache', 'Duchesne': 'rs', 'Price': 'p2',
        'Salt Lake': 'slc', 'Davis': 'slc', 'Tooele': 'tooele', 'Uintah': 'vl',
        'Utah': 'utah', 'Washington': 'washington', 'Weber': 'weber'}

    county_short = county.replace(' County', '')
    code = codes[county_short] if county_short in codes else 'slc'
    response = Response(json.dumps({'city': city, 'county': county, 'state': state, 'zipcode': zipcode, 'code': code}), status=200, mimetype='application/json')
    return response

    
@app.route('/contact', methods=['POST'])
def contact():
    """ Contact form """
    if request.method == 'POST':
        from email.mime.text import MIMEText
        from subprocess import Popen, PIPE

        data = json.loads(request.data)
        contact = data['contact']
        name = contact['name']
        email = contact['email']
        comment = contact['comment']

        msg = MIMEText("Name: {0}\nEmail: {1}\nComment:\n{2}".format(name, email, comment))
        msg["From"] = 'jonstjohn@dev.aircanary.com'
        msg["To"] = "jonstjohn@gmail.com"
        msg["Subject"] = "Air Canary Comment from {0}".format(name)
        p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
        p.communicate(msg.as_string())

        response_data = []
        response = Response(json.dumps(response_data), status=200, mimetype='application/json')
        return response

@app.route('/forecast/<code>', subdomain='api')
@app.route('/api/forecast/<code>')
@cache()
def api_forecast(code):
    """ API forecast """
    site = Site.from_code(code)
    response_data = site.forecast_data()
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.route('/site/<code>', defaults={'samples': 1}, subdomain='api')
@app.route('/site/<code>/<int:samples>', subdomain='api')
@app.route('/api/site/<code>', defaults={'samples': 1})
@app.route('/api/site/<code>/<int:samples>')
@cache()
def api(code, samples):
    """ API site """
    if code == 'all':
        response_data = Site.data_all(samples)
    else:
        site = Site.from_code(code)
        response_data = {'code': site.code, 'name': site.name, 'data': site.data(samples), 'forecast': site.forecast_data()}
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.route('/site', subdomain='api')
@app.route('/api/site')
@cache()
def api_site():
    """ API all sites """
    sites = Site.all_sites()
    response_data = []
    for site in sites:
        response_data.append({'code': site.code, 'name': site.name})
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.route('/area', subdomain='api')
@app.route('/api/area')
def api_areas():
    areas = Area.all(request.args.get('country'), request.args.get('state'), request.args.get('search'))
    response_data = []
    for area in areas:
        response_data.append({'id': area.area_id, 'name': area.name})
    response = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()

def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response

@app.before_request
def csrf_protect():
    if request.method == "POST":
        # Compare header token to cookie token that only our domain can read
        print("X-XSRF-TOKEN: {0}".format(request.headers['X-XSRF-TOKEN']))
        print("XSRF-TOKEN: {0}".format(request.cookies.get('XSRF-TOKEN')))
        if request.headers['X-XSRF-TOKEN'] != request.cookies.get('XSRF-TOKEN'):
            abort(403)
    elif request.method == 'GET':
        # If XSRF token is not set in cookie, set it
        if 'XSRF-TOKEN' not in request.cookies:
            @after_this_request
            def set_csrf_cookie(response):
                response.set_cookie('XSRF-TOKEN', generate_csrf_token())
       
def generate_csrf_token():
    if '_csrf_token' not in session:
        import string
        import random
        session['_csrf_token'] = "".join([random.choice(string.ascii_letters + string.digits) for n in xrange(30)])
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token 


if __name__ == '__main__':
    app.debug = True
    app.run(host = c.settings['configuration']['ip'], port = 8080)

ADMINS = ['jonstjohn@gmail.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'jonstjohn@gmail.com',
                               ADMINS, 'Air Canary Error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
