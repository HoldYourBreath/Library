from library.app import app
from datetime import datetime, timedelta
import library.database as database
from flask import jsonify

BOOK_LOAN_IN_DAYS = 14


def _serialize_loan(item):
    return {
        "book_id": item["book_id"],
        "employee_num": item["employee_number"],
        "loan_date": item["loan_date"],
        "return_date": item["return_date"]
    }

@app.route('/api/loan/', methods=['GET'])
def get_all_loans():
    """
    """
    db_instance = database.get()
    curs = db_instance.execute('select * from loans order by return_date desc')
    loans = curs.fetchall()
    items = [_serialize_loan(loan) for loan in loans]
    return jsonify(items)


@app.route('/api/loan/<int:book_tag>/<int:employee_num>', methods=['GET'])
def loan_book(book_tag, employee_num):
    """
    The front end adds a new book loan using the book tag and employee number.
    """
    loan_date = datetime.now()
    return_date = datetime.now() + timedelta(days=BOOK_LOAN_IN_DAYS)
    print("User {} wants to loan: {}".format(employee_num, book_tag))
    db_instance = database.get()
    curs = db_instance.execute('select book_id from books where tag = ?', (book_tag,))
    book = curs.fetchone()
    if not book:
        response = jsonify({"msg": "No book found with tag {0}".format(book_tag)})
        response.status_code = 404
        return response
    db_instance.execute('insert into loans' \
                        '(book_id, employee_number, loan_date, return_date) ' \
                        'values (?, ?, ?, ?)',
                        (int(book["book_id"]),
                         int(employee_num),
                         int(loan_date.timestamp()),
                         int(return_date.timestamp())
                        ))
    db_instance.commit()
    response = jsonify({"msg": "OK"})
    response.status_code = 200
    return response




