import flask
import uuid
from datetime import datetime

from library.app import app
import library.database as database
import library.ldap as ldap


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
