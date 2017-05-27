from library.app import app
from datetime import datetime, timedelta
import library.database as database
from flask import jsonify

BOOK_LOAN_IN_DAYS = 14


@app.route('/api/loan/<int:book_tag>/<int:employee_num>', methods=['GET'])
def loan_book(book_tag, employee_num):
    """
    The front end adds a new book loan using the book tag and employee number.
    """
    loan_date = datetime.now()
    return_date = datetime.now() + timedelta(days=BOOK_LOAN_IN_DAYS)
    db_instance = database.get()
    curs = db_instance.execute('select book_id, loaned_out from books where tag = ?', (book_tag,))
    book = curs.fetchone()
    if not book:
        response = jsonify({"msg": "No book found with tag {0}".format(book_tag)})
        response.status_code = 404
        return response
    if int(book["loaned_out"]):
        response = jsonify({"msg": "Book already on loan with tag {0}".format(book_tag)})
        response.status_code = 500
        return response
    db_instance.execute('update books ' \
                        'set loaned_out = ?, loaned_by = ?, return_date = ?, loan_date = ? ' \
                        'where tag = ?',
                        (1,
                         int(employee_num),
                         int(loan_date.timestamp()),
                         int(return_date.timestamp()),
                         book_tag))
    db_instance.commit()
    response = jsonify({"msg": "OK"})
    response.status_code = 200
    return response
