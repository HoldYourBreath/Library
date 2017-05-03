import flask
import json

import database
from app import app
import api

@app.route('/')
def root():
    db = database.get()
    curs = db.execute('select * from books order by id desc')
    return flask.render_template('index.html',
                                 books=api._get_books(curs.fetchall()))


@app.route('/add_book')
def add_book_form():
    return flask.render_template('add_book.html')


@app.route('/init_db')
def set_up_db():
    database.init()
    return 'OK'


@app.route('/delete_db')
def remove_db():
    db = database.get()
    db.execute('drop table books')
    return 'OK'


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
