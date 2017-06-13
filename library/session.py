import flask
import uuid
import functools
from datetime import datetime

from library.app import app
import library.database as database
import library.ldap as ldap


def validate_user():
    if 'id' in flask.session:
        db = database.get()
        curs = db.execute('select * from sessions where session_id = (?)',
                          (flask.session['id'],))
        if len(curs.fetchall()) > 0:
            return True

    return False


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not validate_user():
            return flask.redirect(
                flask.url_for('login', next=flask.request.path))
        return f(*args, **kwargs)

    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        user = flask.request.form['signum']
        password = flask.request.form['password']
        if ldap.authenticate(user, password):
            login_time = datetime.now()
            flask.session['id'] = str(uuid.uuid4())
            flask.session['user'] = user
            db = database.get()
            db.execute('INSERT INTO sessions'
                       '(session_id, user_id, login_time, last_activity)'
                       'values (?, ?, ?, ?)',
                       (flask.session['id'],
                        flask.session['user'],
                        login_time,
                        login_time))
            db.commit()

            return flask.redirect('/')
        else:
            return flask.render_template('login.html',
                                         page='login',
                                         header_title='login')

    return flask.render_template('login.html',
                                 page='login',
                                 header_title='login')


@app.route('/logout', methods=['GET'])
def logout():
    flask.session.clear()
    return flask.render_template('logout.html',
                                 page='logout',
                                 header_title='logout')
