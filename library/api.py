import flask
import json

import database
from app import app

books = []


class BookNotFound(Exception):
    pass


@app.route('/api/books', methods=['GET'])
def list_books():
    db = database.get()
    curs = db.execute('select * from books order by book_id desc')
    books = _get_books(curs.fetchall())
    return json.dumps(books)


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):
    book = flask.request.json

    # Check some prerequesite
    if 'isbn' not in book:
        return 'No ISBN present', 400

    # Check if parameters are missing and if so, assign default
    if 'title' not in book:
        book['title'] = ''

    if 'authors' not in book:
        book['authors'] = []

    if 'description' not in book:
        book['description'] = ''

    if 'pages' not in book:
        book['pages'] = 0

    if 'publisher' not in book:
        book['publisher'] = ''

    if 'format' not in book:
        book['format'] = ''

    if 'publication_date' not in book:
        book['publication_date'] = ''

    # Check integer parameter constraints
    try:
        int(book['isbn'])
        int(book['pages'])
    except ValueError:
        return 'Non number in parameter where number is expected', 400

    # First delete any previous record, then add a new
    db = database.get()
    db.execute('delete from books where tag=?', (int(book_id),))
    db.execute('insert into books' \
               '(tag, isbn, title, pages, publisher, format,' \
               'publication_date, description)' \
               'values (?, ?, ?, ?, ?, ?, ?, ?)',
               (int(book_id),
                int(book['isbn']),
                book['title'],
                book['pages'],
                book['publisher'],
                book['format'],
                book['publication_date'],
                book['description']))
    db.commit()
    _add_authors(book_id, book['authors'])
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
                     'isbn': book['isbn'],
                     'title': book['title'],
                     'authors': _get_authors(book['book_id']),
                     'pages': book['pages'],
                     'format': book['format'],
                     'publisher': book['publisher'],
                     'publication_date': book['publication_date'],
                     'description': book['description']}
        books.append(json_book)

    return books

def _add_authors(book_id, authors):
    db = database.get()
    curs = db.execute('select * from books where tag = ?', (book_id,))
    book = curs.fetchone()

    for author in authors:
        curs = db.execute('insert into authors (book_id, name) values (?, ?)',
                          (book['book_id'], author))

    db.commit()

def _get_authors(book_id):
    db = database.get()
    curs = db.execute('select * from authors where book_id = ?', (book_id,))

    authors = []
    for author in curs.fetchall():
        authors.append(author['name'])

    return authors
