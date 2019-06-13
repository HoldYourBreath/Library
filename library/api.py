import flask
from flask import jsonify

import library.database as database
import library.loan as loan
import library.session as session
from library.app import app
from library.books import Books, Book, BookError, BookNotFound


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

