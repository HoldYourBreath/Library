import flask
from flask import jsonify

import library.database as database
import library.loan as loan
from library.app import app


class BookNotFound(Exception):
    pass


@app.route('/api/books', methods=['GET'])
def list_books():
    db = database.get()
    wheres = []
    query_params = []

    if 'isbn' in flask.request.args:
        wheres.append(' WHERE books.isbn = ?')
        query_params.append(flask.request.args['isbn'])

    if 'title' in flask.request.args:
        wheres.append(' WHERE books.title LIKE ?')
        query_params.append('%' + flask.request.args['title'] + '%')

    if 'description' in flask.request.args:
        wheres.append(' WHERE books.description LIKE ?')
        query_params.append('%' + flask.request.args['description'] + '%')

    if 'room_id' in flask.request.args:
        wheres.append(' WHERE books.room_id = ?')
        query_params.append(flask.request.args['room_id'])

    if 'site' in flask.request.args:
        wheres.append(' WHERE sites.site_name LIKE ?')
        query_params.append('%' + flask.request.args['site'] + '%')

    if 'loaned' in flask.request.args:
        loaned = flask.request.args['loaned'].lower()
        if 'true' in loaned:
            wheres.append(' WHERE loans.loan_id IS NOT NULL')
        elif 'false' in loaned:
            wheres.append(' WHERE loans.loan_id IS NULL')

    if 'room' in flask.request.args:
        wheres.append(' WHERE rooms.room_name LIKE ?')
        query_params.append('%' + flask.request.args['room'] + '%')

    where_conditions = ''
    if len(wheres) > 0:
        for where in wheres:
            where_conditions += where.replace('WHERE', 'AND')

    query = 'SELECT * FROM books ' \
            'LEFT JOIN loans USING (book_id) ' \
            'LEFT JOIN rooms USING (room_id) ' \
            'LEFT JOIN sites USING (site_id) ' \
            'WHERE loans.return_date IS NULL ' \
            '{} GROUP BY isbn ORDER BY book_id '

    query = query.format(where_conditions)

    curs = db.execute(query, tuple(query_params))

    books = _get_books(curs.fetchall())

    return jsonify(books)


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):
    '''
    Add or update new book

    This method will add a new book with a certein tag
    or simply updating existing book with a tag if it
    already exists
    '''

    book = flask.request.get_json()

    # Check some prerequesite
    if 'isbn' not in book:
        return 'No ISBN present', 400
    elif 'room_id' not in book:
        return 'No room_id present', 400

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

    # First delete any previous record, store old book id
    # and then add a new
    old_book_id = None
    db = database.get()
    old_book_cursor = db.execute('select book_id from books where tag=?',
                                 (int(book_id),))
    old_book = old_book_cursor.fetchall()
    if len(old_book) > 0:
        old_book_id = old_book[0]['book_id']
        db.execute('delete from books where book_id=?',
                   (old_book_id,))
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
    if old_book_id is not None:
        # This book with this tag exister before, use same book_id
        db.execute('UPDATE books SET book_id = ? WHERE tag = ?',
                   (old_book_id, book_id))
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


@app.route('/api/books/<int:book_id>/loan', methods=['GET'])
def get_loan_for_book(book_id):
    """ Get the loan for this book """
    try:
        return jsonify(loan.by_book_id(book_id))
    except loan.LoanNotFound:
        response = jsonify({'msg': 'No loan found for this book'})
        response.status_code = 404
        return response


@app.route('/api/books/<int:book_id>/loan', methods=['PUT'])
def loan_book(book_id):
    """ Loan this book """
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing json data in put request.'})
        response.status_code = 400
        return response
    elif 'user_id' not in put_data:
        response = jsonify({'msg': 'Missing user_id in put request.'})
        response.status_code = 400
        return response

    try:
        return jsonify(loan.add(book_id, put_data['user_id']))
    except loan.LoanNotAllowed:
        response = jsonify({'msg': 'Loan allready exists for this book'})
        response.status_code = 403
        return response


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
