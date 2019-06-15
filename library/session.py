import flask
from flask import jsonify
import uuid
import functools
from datetime import datetime

from library.app import app
import library.database as database
import library.ldap as ldap
from library.config import config

AUTHENTICATE = True
OVERRIDE_ADMIN = False


class SessionNotFound(Exception):
    pass


def is_admin(user):
    app.logger.debug('test if user ({}) has admin rights'.format(user))
    if user == config.get('General', 'admin'):
        app.logger.debug('User listed as admin in config')
        return True

    db = database.get()
    curs = db.execute('SELECT * FROM admins WHERE user_id = ?',
                      (user,))
    admins = curs.fetchall()
    if len(admins):
        app.logger.debug('User listed as admin in database')
        return True

    app.logger.debug('User not admin')
    return False


def validate_user(admin_required):
    if 'session_id' in flask.session:
        db = database.get()

        curs = db.execute('select * from sessions where session_id = (?)',
                          (flask.session['session_id'],))
        sessions = curs.fetchall()

        if len(sessions) > 0 and \
           sessions[0]['secret'] == flask.session['session_secret']:
            if admin_required:
                return is_admin(sessions[0]['user_id'])
            else:
                return True
    return False


def admin_required(f):
    """
    admin required decorator

    Decorator to restrict a resource to admin users only
    """
    admin_required = True

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not OVERRIDE_ADMIN and not validate_user(admin_required):
            response = jsonify({'err': 'Authentication failed'})
            response.status_code = 401
            return response

        return f(*args, **kwargs)

    return wrapper


def login_required(f):
    """
    Login required decorator

    Decorator to restrict a resource to logged in users only
    """
    admin_required = False

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not validate_user(admin_required):
            response = jsonify({'err': 'Authentication failed'})
            response.status_code = 401
            return response

        return f(*args, **kwargs)

    return wrapper


@app.route('/api/login/validate', methods=['POST'])
def api_validate():
    user_credentials = flask.request.get_json()
    user = user_credentials['session_id']
    session_secret = user_credentials['secret']
    session_id = validate_session(user, session_secret)
    if not session_id:
        response = jsonify({'err': 'Invalid session'})
        response.status_code = 401
    else:
        response = jsonify({'msg': 'Session correct'})
        response.status_code = 200
    return response


@app.route('/api/login', methods=['POST'])
def api_login():
    user_credentials = flask.request.get_json()
    for param in ['user', 'password']:
        if param not in user_credentials:
            response = jsonify({'err': 'Missing {}'.format(param)})
            response.status_code = 400
            return response

    user = user_credentials['user']
    password = user_credentials['password']
    if not AUTHENTICATE or ldap.authenticate(user, password):
        session_id = create_session(user)
        session_secret = get_secret(session_id)
        response = jsonify({'session_id': session_id,
                            'session_secret': session_secret})
        flask.session['session_id'] = session_id
        flask.session['session_secret'] = session_secret
    else:
        response = jsonify({'err': 'Authentication failed'})
        response.status_code = 401
    return response


def validate_session(user: int, secret: str) -> str:
    """
    Used to validate a session.

    :param user:
    :param session_secret:
    :return: session_id if valid, empty string otherwise.
    """
    db = database.get()
    curs = db.execute('SELECT session_id FROM sessions '
                      'WHERE session_id = ? AND secret = ?',
                      (user, secret))
    previous_session = curs.fetchone()
    if previous_session:
        return previous_session['session_id']
    return ''


def get_session_for_user(user: str) -> str:
    db = database.get()
    curs = db.execute('SELECT session_id FROM sessions '
                      'WHERE user_id = ?',
                      (user,))
    previous_session = curs.fetchone()
    if previous_session:
        return previous_session['session_id']
    return ''


def get_secret(session_id: int) -> str:
    db = database.get()
    curs = db.execute('SELECT secret FROM sessions '
                      'WHERE session_id = ?',
                      (session_id,))
    session = curs.fetchone()
    if not session:
        raise SessionNotFound

    return session['secret']


def create_session(user: str) -> str:
    login_time = datetime.now()
    secret = str(uuid.uuid4())
    db = database.get()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO sessions'
        '(secret, user_id, login_time, last_activity)'
        'values (?, ?, ?, ?)',
        (secret,
         user,
         login_time,
         login_time))
    session_id = cursor.lastrowid
    db.commit()
    return session_id


@app.route('/api/login/delete', methods=['POST'])
def delete_session():
    user_credentials = flask.request.get_json()
    user = user_credentials['session_id']
    secret = user_credentials['secret']
    session_id = validate_session(user, secret)
    if not session_id:
        response = jsonify({'err': 'Authentication failed'})
        response.status_code = 401
        return response

    db = database.get()
    cursor = db.cursor()
    cursor.execute(
        'DELETE FROM sessions '
        'WHERE session_id = ?',
        (session_id, ))
    db.commit()

    response = jsonify({'msg': 'Session deleted'})
    return response
