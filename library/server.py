import flask
from flask import send_from_directory
import json

import library.database as database
from library.app import app
import library.api as api
import library.goodreads_interface as goodreads_interface
import library.user_lookup


@app.route('/')
def root():
    db = database.get()
    curs = db.execute('select * from books order by book_id desc')
    return flask.render_template('index.html',
                                 header_title="We got books!",
                                 books=api._get_books(curs.fetchall()))


@app.route('/add_book')
def add_book_form():
    return flask.render_template('add_book.html',
                                 header_title="Add book!")


@app.route('/init_db')
def set_up_db():
    database.init()
    return 'OK'


@app.route('/delete_db')
def remove_db():
    db = database.get()
    db.execute('drop table if exists books')
    db.execute('drop table if exists authors')
    return 'OK'


@app.route('/static/<path:path>')
def serve_static(path):
    print("path: {}".format(path))
    return send_from_directory('static', path)


def run():
    app.config['DEBUG'] = True
    app.run()


if __name__ == "__main__":
    run()
