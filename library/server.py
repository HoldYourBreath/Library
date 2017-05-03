import flask
import json

import database
from app import app

books = []


class BookNotFound(Exception):
    pass


@app.route('/')
def root():
    db = database.get()
    curs = db.execute('select * from books order by id desc')
    return flask.render_template('index.html',
                                 books=_get_books(curs.fetchall()))


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


@app.route('/api/books', methods=['GET'])
def list_books():
    db = database.get()
    curs = db.execute('select * from books order by id desc')
    books = _get_books(curs.fetchall())
    return json.dumps(books)


@app.route('/api/books/<book_id>', methods=['PUT'])
def get_books(book_id):
    isbn = flask.request.form['isbn']
    db = database.get()
    db.execute('delete from books where tag=?', (int(book_id),))
    db.execute('insert into books (tag, isbn) values (?, ?)',
               (int(book_id), int(isbn)))
    db.commit()
    return json.dumps(_get_book(book_id))


@app.route('/api/books/<book_id>', methods=['GET'])
def get_single_book(book_id):
    try:
        return json.dumps(_get_book(book_id))
    except BookNotFound:
        return 'Not found', 404


def _get_book(book_id):
    db = database.get()
    curs = db.execute('select * from books where tag = ?', (book_id,))

    book = curs.fetchall()
    if len(book) == 0:
        raise BookNotFound

    return _get_books(book)[0]


def _get_books(rows):
    books = []
    for book in rows:
        json_book = {'tag': book['tag'],
                     'isbn': book['isbn']}
        books.append(json_book)

    return books


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
