import flask
from flask import jsonify

import library.database as database
import library.loan as loan
import library.session as session
from library.app import app
from library.books import Books, Book, BookError, BookNotFound, BookDescriptor


@app.route('/api/books/ebids', methods=['GET'])
def list_ebooks():
    '''
    List all books

    List all available books. Query params can be used to search
    for different books
    '''

    return jsonify(Books.get(flask.request.args).marshal())


@app.route('/api/books/ebids/<int:book_id>', methods=['GET'])
def get_single_ebook(book_id):
    try:
        return jsonify(Book.get(book_id).marshal())
    except BookNotFound:
        response = jsonify(
            {"msg": "Book with id {} not found".format(book_id)})
        response.status_code = 404
        return response


@app.route('/api/books/ebids/<int:book_id>', methods=['PUT'])
@session.admin_required
def put_single_ebook(book_id):
    book_request = flask.request.get_json()

    try:
        book = Book(book_id, **book_request)
        if not book.exists():
            book.add()
        else:
            book.update()
    except BookError as e:
        return e.msg, 400

    return jsonify(book.marshal())
