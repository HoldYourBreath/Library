import flask
from flask import send_from_directory
import json
import uuid
from datetime import datetime

import library.database as database
from library.app import app
import library.api as api
import library.goodreads_interface as goodreads_interface
import library.user_lookup
import library.api_loan
import library.ldap as ldap
import library.api_location as api_location


@app.route('/')
def root():
    db = database.get()
    curs = db.execute('select * from books order by book_id desc')
    return flask.render_template('index.html',
                                 page='books',
                                 header_title="We got books!",
                                 books=api._get_books(curs.fetchall()))


@app.route('/add_book')
def add_book_form():
    return flask.render_template('add_book.html',
                                 page='add_book',
                                 rooms=api_location.get_rooms(),
                                 header_title="Add book!")


@app.route('/init_db')
def set_up_db():
    database.init()
    return 'OK'


@app.route('/delete_db')
def remove_db():
    db = database.get()
    db.execute('DROP TABLE IF EXISTS books')
    db.execute('DROP TABLE IF EXISTS authors')
    db.execute('DROP TABLE IF EXISTS sites')
    db.execute('DROP TABLE IF EXISTS rooms')
    db.execute('DROP TABLE IF EXISTS loans')
    db.commit()
    return 'OK'


@app.route('/loan_book')
def render_loan_book():
    return flask.render_template('loan_book.html',
                                 header_title="Loan book!")


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


@app.route('/static/<path:path>')
def serve_static(path):
    print("path: {}".format(path))
    return send_from_directory('static', path)


def run():
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0')


if __name__ == "__main__":
    run()
