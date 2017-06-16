import flask
from flask import jsonify

import library.database as database
from library.app import app


class BookNotFound(Exception):
    pass


@app.route('/api/books', methods=['GET'])
def list_books():
    db_instance = database.get()
    wheres = []
    query_params = []
    where_conditions = ''

    if 'isbn' in flask.request.args:
        wheres.append(' WHERE isbn = ?')
        query_params.append(flask.request.args['isbn'])

    if 'title' in flask.request.args:
        wheres.append(' WHERE title LIKE ?')
        query_params.append('%' + flask.request.args['title'] + '%')

    if 'description' in flask.request.args:
        wheres.append(' WHERE description LIKE ?')
        query_params.append('%' + flask.request.args['description'] + '%')

    if len(wheres) == 1:
        where_conditions = wheres[0]
    elif len(wheres) > 1:
        where_conditions = wheres.pop(0)
        for where in wheres:
            where_conditions += where.replace('WHERE', 'AND')

    query = 'SELECT * FROM books {} GROUP BY isbn ORDER BY book_id '
    query = query.format(where_conditions)

    curs = db_instance.execute(query, tuple(query_params))

    books = _get_books(curs.fetchall())
    return jsonify(books)


@app.route('/api/books_on_loan', methods=['GET'])
def list_books_on_loan():
    """
    List all books that are out on loan
    """
    db_instance = database.get()
    curs = db_instance.execute('SELECT * from books '
                               'JOIN loans USING (book_id) '
                               'ORDER BY book_id DESC')
    books = _get_books(curs.fetchall())
    return jsonify(books)


@app.route('/api/books_available', methods=['GET'])
def list_available_books():
    """
    List all books that are not out on loan
    """
    db_instance = database.get()
    curs = db_instance.execute(
        'SELECT * '
        'FROM books LEFT OUTER JOIN loans using (book_id) '
        'WHERE loan_date IS NULL ORDER by book_id DESC'
    )
    books = _get_books(curs.fetchall())
    return jsonify(books)


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):
    book = flask.request.get_json()

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

    if 'thumbnail' not in book:
        book['thumbnail'] = ''

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
    curs = db.execute('select * from books where tag = ?',
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
                     'thumbnail': book['thumbnail']}
        try:
            json_book['return_date'] = book['return_date']
            json_book['loan_date'] = book['loan_date']
            json_book['employee_number'] = book['employee_number']
        except IndexError:
            pass
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
