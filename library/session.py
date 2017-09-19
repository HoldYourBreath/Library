import flask
from flask import jsonify
import uuid
import functools
from datetime import datetime

from library.app import app
import library.database as database
import library.ldap as ldap

AUTHENTICATE = True


def is_admin(user):
    db = database.get()
    curs = db.execute('SELECT * FROM admins WHERE user_id = ?',
                      (user,))
    if len(curs.fetchall()):
        return True

    return False


def validate_user(admin_required):
    if 'signum' in flask.session:
        db = database.get()

        curs = db.execute('select * from sessions where user_id = (?)',
                          (flask.session['signum'],))
        sessions = curs.fetchall()
        if len(sessions) > 0 and \
           sessions[0]['secret'] == flask.session['secret']:
            if admin_required:
                return is_admin(flask.session['signum'])
            else:
                return True
    return False


def login_required(*args, admin_required=False):
    """
    Login required decorator

    Decorator to restrict a resource to logged in users only


    Keyword arguments:
    admin -- Require that the user is admin
    """
    def _login_required(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not validate_user(admin_required):
                response = jsonify({'err': 'Authentication failed'})
                response.status_code = 401
                return response

            return f(*args, **kwargs)

        return wrapper

    if len(args) == 1 and callable(args[0]):
        # Assume decorator called without argument
        return _login_required(args[0])
    elif len(args) > 0:
        raise TypeError('Invalid use of decorator')

    return _login_required


@app.route('/api/login/validate', methods=['POST'])
def api_validate():
    user_credentials = flask.request.get_json()
    user = user_credentials['signum']
    secret = user_credentials['secret']
    session_id = validate_session(user, secret)
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
    user = user_credentials['signum']
    password = user_credentials['password']
    if not AUTHENTICATE or ldap.authenticate(user, password):
        secret = create_session(user)
        response = jsonify({'secret': secret})
    else:
        response = jsonify({'err': 'Authentication failed'})
        response.status_code = 401
    return response


def validate_session(user: str, secret: str) -> str:
    """
    Used to validate a session.

    :param user:
    :param secret:
    :return: session_id if valid, empty string otherwise.
    """
    db = database.get()
    curs = db.execute('SELECT session_id FROM sessions '
                      'WHERE user_id = ? AND secret = ?',
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


def create_session(user: str) -> str:
    login_time = datetime.now()
    secret = str(uuid.uuid4())
    previous_session_id = get_session_for_user(user)
    db = database.get()
    cursor = db.cursor()
    if previous_session_id:
        cursor.execute(
            'UPDATE sessions '
            'SET secret = ? , login_time = ? , last_activity = ? '
            'WHERE session_id = ?',
            (secret,
             login_time,
             login_time,
             previous_session_id))
    else:
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO sessions'
            '(secret, user_id, login_time, last_activity)'
            'values (?, ?, ?, ?)',
            (secret,
             user,
             login_time,
             login_time))
    db.commit()
    return secret


@app.route('/api/login/delete', methods=['POST'])
def delete_session():
    user_credentials = flask.request.get_json()
    user = user_credentials['signum']
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
