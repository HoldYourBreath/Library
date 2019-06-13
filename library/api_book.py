import flask
from flask import jsonify

import library.session as session
from library.app import app
from library.books import Books, Book, BookError, \
                          BookNotFound, BookDescriptor, BookDescriptors

import library.loan as loan


@app.route('/api/books/ebids', methods=['GET'])
def list_ebooks():
    '''
    List all books

    List all available books. Query params can be used to search
    for different books
    '''

    return jsonify(Books.get(flask.request.args).marshal())


@app.route('/api/books/ebids/<int:book_id>', methods=['GET'])
def get_single_book(book_id):
    try:
        return jsonify(Book.get(book_id).marshal())
    except BookNotFound:
        response = jsonify(
            {"msg": "Book with id {} not found".format(book_id)})
        response.status_code = 404
        return response


@app.route('/api/books/ebids/<int:book_id>', methods=['PUT'])
@session.admin_required
def put_single_book(book_id):
    book_request = flask.request.get_json()

    try:
        book = Book(book_id, **book_request)
        if not book.exists(book.book_id):
            book.add()
        else:
            book.update()
    except BookError as e:
        return e.msg, 400

    return jsonify(book.marshal())


@app.route('/api/books/ebids/<string:book_id>', methods=['PUT'])
@session.admin_required
def put_single_book_string(book_id):
    return "Need integer", 400


@app.route('/api/books/ebids/<int:book_id>/loan', methods=['GET'])
def get_loan_for_book(book_id):
    '''Get loan for this book'''
    if not Book.exists(book_id):
        response = jsonify({'msg': 'Book not found'})
        response.status_code = 404
        return response

    try:
        return jsonify(loan.by_book_id(book_id))
    except loan.LoanNotFound:
        response = jsonify({'msg': 'No loan found for this book'})
        response.status_code = 404
        return response


@app.route('/api/books/ebids/<int:book_id>/loan', methods=['PUT'])
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

    if not Book.exists(book_id):
        response = jsonify({'msg': 'Book not found'})
        response.status_code = 404
        return response

    try:
        return jsonify(loan.add(book_id, put_data['user_id']))
    except loan.LoanNotAllowed:
        response = jsonify({'msg': 'Loan already exists for this book'})
        response.status_code = 403
        return response


@app.route('/api/books/ebids/<int:book_id>/loan', methods=['DELETE'])
def return_book(book_id):
    """ Return current loan for this book """
    if not Book.exists(book_id):
        response = jsonify({'msg': 'Book not found'})
        response.status_code = 404
        return response

    try:
        return jsonify(loan.remove_on_book(book_id))
    except loan.LoanNotFound:
        response = jsonify({'msg': 'Loan not found'})
        response.status_code = 404
        return response


@app.route('/api/books/<int:isbn>', methods=['GET'])
def get_single_book_descriptor(isbn):
    try:
        return jsonify(BookDescriptor.get(isbn).marshal())
    except BookNotFound:
        response = jsonify(
            {"msg": "Book with isbn {} not found".format(isbn)})
        response.status_code = 404
        return response


@app.route('/api/books/<int:isbn>', methods=['PUT'])
@session.admin_required
def put_book(isbn):
    '''
    Add new or update existing book

    This method will add a new book with a certein book_id
    or simply updating existing book with if it already exists
    '''
    book_request = flask.request.get_json()

    try:
        book = BookDescriptor(**book_request)
    except BookError as e:
        return e.msg, 400

    try:
        if book.exists(book.book_id):
            # Update existing book
            book.update()
        else:
            # Create a new book
            book.add()

    except BookError as e:
        return e.msg, 400

    return jsonify(book.marshal())


@app.route('/api/books', methods=['GET'])
def list_books():
    '''
    List all books

    List all available books. Query params can be used to search
    for different books
    '''

    return jsonify(BookDescriptors.get(flask.request.args).marshal())
