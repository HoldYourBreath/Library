import flask
from flask import send_from_directory

import library.database as database
from library.app import app
import library.api as api
import library.goodreads_interface as goodreads_interface
import library.user_lookup
import library.api_loan
import library.api_location as api_location
import library.session as session


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
                                 sites=api_location._get_sites(),
                                 header_title="Add book!")


@app.route('/init_db')
def set_up_db():
    database.init()
    return 'OK'


@app.route('/delete_db')
def remove_db():
    database.init()
    return 'OK'


@app.route('/loan_book')
def render_loan_book():
    return flask.render_template('loan_book.html',
                                 header_title="Loan book!")


@app.route('/static/<path:path>')
def serve_static(path):
    print("path: {}".format(path))
    return send_from_directory('static', path)


def run(args):
    if args.fake_auth:
        print('Faking authentication')
        session.AUTHENTICATE = False
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0')


if __name__ == "__main__":
    run()
