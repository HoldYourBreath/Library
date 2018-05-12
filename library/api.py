import flask
from flask import jsonify

import library.database as database
import library.loan as loan
import library.session as session
from library.app import app
from library.books import Book, BookError, BookNotFound


@app.route('/api/books', methods=['GET'])
def list_books():
    '''
    List all books

    List all available books. Query params can be used to search
    for different books
    '''
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

    if 'site_id' in flask.request.args:
        wheres.append(' WHERE sites.site_id = ?')
        query_params.append(flask.request.args['site_id'])

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
@session.admin_required
def put_book(book_id):
    '''
    Add new or update existing book

    This method will add a new book with a certein book_id
    or simply updating existing book with if it already exists
    '''
    book_request = flask.request.get_json()

    try:
        book = Book(book_id, **book_request)
    except BookError as e:
        return e.msg, 400

    authors = []
    if 'authors' in book_request:
        authors = book_request['authors']

    try:
        if book.exists():
            # Update existing book
            book.update()
            book.update_authors(authors)
        else:
            # Create a new book
            book.add()
            book.add_authors(authors)

        return jsonify(book.marshal())
    except BookError as e:
        return e.msg, 400

    return jsonify(book.marshal())


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_single_book(book_id):
    try:
        return jsonify(Book.get(book_id).marshal())
    except BookNotFound:
        response = jsonify(
            {"msg": "Book with id {} not found".format(book_id)})
        response.status_code = 404
        return response


def _get_books(rows):
    books = []
    for book in rows:
        json_book = {'id': book['book_id'],
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
    '''Get loan for this book'''
    if not _book_exist(book_id):
        response = jsonify({'msg': 'Book not found'})
        response.status_code = 404
        return response

    try:
        return jsonify(loan.by_book_id(book_id))
    except loan.LoanNotFound:
        response = jsonify({'msg': 'No loan found for this book'})
        response.status_code = 404
        return response


@app.route('/api/books/<int:book_id>/loan', methods=['PUT'])
def loan_book(book_id):
    '''Loan this book'''
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing json data in put request.'})
        response.status_code = 400
        return response
    elif 'user_id' not in put_data:
        response = jsonify({'msg': 'Missing user_id in put request.'})
        response.status_code = 400
        return response

    if not _book_exist(book_id):
        response = jsonify({'msg': 'Book not found'})
        response.status_code = 404
        return response

    try:
        return jsonify(loan.add(book_id, put_data['user_id']))
    except loan.LoanNotAllowed:
        response = jsonify({'msg': 'Loan already exists for this book'})
        response.status_code = 403
        return response


@app.route('/api/books/<int:book_id>/loan', methods=['DELETE'])
def return_book(book_id):
    """ Return current loan for this book """
    if not _book_exist(book_id):
        response = jsonify({'msg': 'Book not found'})
        response.status_code = 404
        return response

    try:
        return jsonify(loan.remove_on_book(book_id))
    except loan.LoanNotFound:
        response = jsonify({'msg': 'Loan not found'})
        response.status_code = 404
        return response


def _update_authors(book_id, authors):
    db = database.get()
    db.execute('DELETE FROM authors WHERE book_id = ?',
               (book_id,))
    _add_authors(book_id, authors)


def _add_authors(book_id, authors):
    db = database.get()
    for author in authors:
        db.execute(
            'INSERT INTO authors (book_id, name) VALUES (?, ?)',
            (book_id, author))

    db.commit()


def _get_authors(book_id):
    db = database.get()
    curs = db.execute('SELECT * FROM authors WHERE book_id = ?',
                      (book_id,))

    authors = []
    for author in curs.fetchall():
        authors.append(author['name'])

    return authors


def _book_exist(book_id):
    db = database.get()
    curs = db.execute('SELECT * FROM books WHERE book_id = ?',
                      (book_id,))

    books = curs.fetchall()
    if len(books) == 0:
        return False

    return True
