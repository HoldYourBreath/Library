import flask
from flask import jsonify

import library.database as database
from library.app import app


class BookNotFound(Exception):
    pass


@app.route('/api/books', methods=['GET'])
def list_books():
    db = database.get()
    wheres = []
    query_params = []

    if 'isbn' in flask.request.args:
        wheres.append(' WHERE isbn = ?')
        query_params.append(flask.request.args['isbn'])

    if 'title' in flask.request.args:
        wheres.append(' WHERE title LIKE ?')
        query_params.append('%' + flask.request.args['title'] + '%')

    if 'description' in flask.request.args:
        wheres.append(' WHERE description LIKE ?')
        query_params.append('%' + flask.request.args['description'] + '%')

    if 'loaned' in flask.request.args:
        loaned = flask.request.args['loaned'].lower()
        if 'true' in loaned:
            wheres.append(' WHERE loans.loan_id IS NOT NULL')
        elif 'false' in loaned:
            wheres.append(' WHERE loans.loan_id IS NULL')

    where_conditions = ''
    if len(wheres) > 0:
        for where in wheres:
            where_conditions += where.replace('WHERE', 'AND')

    query = 'SELECT * FROM books ' \
            'LEFT JOIN loans USING (book_id) ' \
            'WHERE loans.return_date IS NULL ' \
            '{} GROUP BY isbn ORDER BY book_id '

    query = query.format(where_conditions)

    curs = db.execute(query, tuple(query_params))

    books = _get_books(curs.fetchall())

    return jsonify(books)


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):
    book = flask.request.get_json()

    # Check some prerequesite
    if 'isbn' not in book:
        return 'No ISBN present', 400

    # Defaul parameters
    defaults = {'title': '',
                'authors': [],
                'description': '',
                'thumbnail': '',
                'pages': 0,
                'publisher': '',
                'format': '',
                'publication_date': ''}

    # Check if parameters are missing and if so, assign default
    for key, value in defaults.items():
        if key not in book:
            book[key] = value

    # Check integer parameter constraints
    try:
        int(book['isbn'])
        int(book['pages'])
    except ValueError:
        return 'Non number in parameter where number is expected', 400

    # First delete any previous record, then add a new
    db = database.get()
    db.execute('delete from books where tag=?', (int(book_id),))
    db.execute('insert into books'
               '(tag, isbn, room_id, title, pages, publisher, format,'
               'publication_date, description, thumbnail)'
               'values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               (int(book_id),
                int(book['isbn']),
                int(book['room_id']),
                book['title'],
                book['pages'],
                book['publisher'],
                book['format'],
                book['publication_date'],
                book['description'],
                book['thumbnail']
                ))
    db.commit()
    _add_authors(book_id, book['authors'])
    return jsonify(_get_book(book_id))


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_single_book(book_id):
    try:
        return jsonify(_get_book(book_id))
    except BookNotFound:
        response = jsonify(
            {"msg": "Book with id {} not found".format(book_id)})
        response.status_code = 404
        return response


def _get_book(book_id):
    db = database.get()
    curs = db.execute('SELECT * FROM books '
                      'LEFT JOIN loans USING (book_id) '
                      'WHERE loans.return_date IS NULL AND books.tag = ?',
                      (book_id,))

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
                     'room_id': book['room_id'],
                     'pages': book['pages'],
                     'format': book['format'],
                     'publisher': book['publisher'],
                     'publication_date': book['publication_date'],
                     'description': book['description'],
                     'thumbnail': book['thumbnail'],
                     'loaned':
                     'loan_id' in book.keys() and book['loan_id'] is not None}
        books.append(json_book)
    return books


def _add_authors(book_id, authors):
    db = database.get()
    curs = db.execute('select * from books where tag = ?',
                      (book_id,))
    book = curs.fetchone()

    for author in authors:
        curs = db.execute(
            'insert into authors (book_id, name) values (?, ?)',
            (book['book_id'], author))

    db.commit()


def _get_authors(book_id):
    db = database.get()
    curs = db.execute('select * from authors where book_id = ?',
                      (book_id,))

    authors = []
    for author in curs.fetchall():
        authors.append(author['name'])

    return authors
