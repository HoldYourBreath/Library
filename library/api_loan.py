from library.app import app
from datetime import datetime, timedelta
import library.database as database
from flask import json, jsonify

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
    db = database.get()
    curs = db.execute('select * from loans order by return_date desc')
    loans = curs.fetchall()
    print(loans)
    response = jsonify({"msg": "Book not found"})
    response.status_code = 200
    items = [_serialize_loan(loan) for loan in loans]
    return jsonify(items)


@app.route('/api/loan/<int:book_id>/<int:employee_num>', methods=['GET'])
def loan_book(book_id, employee_num):
    loan_date = datetime.now()
    return_date = datetime.now() + timedelta(days=BOOK_LOAN_IN_DAYS)
    print("User {} wants to loan: {}".format(employee_num, book_id))
    db = database.get()
    db.execute('insert into loans' \
               '(book_id, employee_number, loan_date, return_date) ' \
               'values (?, ?, ?, ?)',
               (int(book_id),
                int(employee_num),
                int(loan_date.timestamp()),
                int(return_date.timestamp())
                ))
    db.commit()
    response = jsonify({"msg": "OK"})
    response.status_code = 200
    return response




