import sqlite3
from library.app import app
from datetime import datetime, timedelta
import library.database as database
import flask
from flask import jsonify

BOOK_LOAN_IN_DAYS = 14


def _serialize_loan(item):
    return {
        "book_id": item["book_id"],
        "employee_num": item["employee_number"],
        "loan_date": item["loan_date"],
        "return_date": item["return_date"]
    }


@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    """
    """
    db_instance = database.get()
    curs = db_instance.execute('select * from loans order by due_date desc')
    loans = curs.fetchall()
    items = [_serialize_loan(loan) for loan in loans]
    return jsonify(items)


@app.route('/api/loans/due', methods=['GET'])
def get_all_due_loans():
    """
    Get all loans not yet returned.
    """
    db_instance = database.get()
    curs = db_instance.execute('select * from loans order by due_date desc')
    loans = curs.fetchall()
    items = [_serialize_loan(loan) for loan in loans]
    return jsonify(items)


@app.route('/api/loan/<int:book_tag>', methods=['PUT'])
def loan_book(book_tag):
    """
    The front end adds a new book loan using the book tag and employee number.
    """
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing json data in put request.'})
        response.status_code = 500
        return response
    elif 'employee_num' not in put_data:
        response = jsonify({'msg': 'Missing employee_number in put request.'})
        response.status_code = 500
        return response
    loan_date = datetime.now()
    due_date = datetime.now() + timedelta(days=BOOK_LOAN_IN_DAYS)
    db_instance = database.get()
    curs = db_instance.execute('SELECT book_id FROM books where tag = ?',
                               (book_tag,))
    book = curs.fetchone()
    if not book:
        response = jsonify(
            {"msg": "No book found with tag {0}".format(book_tag)})
        response.status_code = 404
        return response
    try:
        db_instance.execute(
            'INSERT INTO loans'
            '(book_id, employee_number, loan_date, due_date) '
            'VALUES (?, ?, ?, ?)',
            (int(book['book_id']),
             int(put_data['employee_num']),
             int(loan_date.timestamp()),
             int(due_date.timestamp()))
        )
        db_instance.commit()
        response = jsonify({"msg": "OK"})
        response.status_code = 200
    except sqlite3.IntegrityError:
        response = jsonify({"msg": "Book already checked "
                                   "out {0}".format(book_tag)})
        response.status_code = 500
    return response


@app.route('/api/loan/<int:book_tag>', methods=['DELETE'])
def check_in_book(book_tag):
    """
    Set the return date to null to return a book.
    """
    db_instance = database.get()
    db_instance.execute('DELETE FROM loans WHERE EXISTS '
                        '(SELECT book_id FROM books WHERE tag = ?)',
                        (int(book_tag),))
    db_instance.commit()
    response = jsonify({"msg": "OK"})
    response.status_code = 200
    return response
