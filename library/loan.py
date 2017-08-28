from datetime import datetime, timedelta

import library.database as database


class LoanError(Exception):
    pass


class LoanNotFound(Exception):
    pass


def _serialize_loan(item):
    return {
        "book_id": item["book_id"],
        "user_id": item["user_id"],
        "loan_date": item["loan_date"],
        "return_date": item["return_date"]
    }


def get(loan_id):
    '''Get a loan'''
    db_instance = database.get()
    curs = db_instance.execute('select * from loans where loan_id = ?',
                               (loan_id,))
    loan = curs.fetchone()

    if not loan:
        raise LoanNotFound

    return _serialize_loan(loan)


def get_all(loan_id):
    '''Get all loans'''
    db_instance = database.get()
    curs = db_instance.execute('select * from loans')
    loans = curs.fetchall()
    return [_serialize_loan(loan) for loan in loans]


def by_book_id(book_id, only_active=False):
    '''Get a loan by book id'''
    db_instance = database.get()
    curs = db_instance.execute('select * from loans where book_id = ?',
                               (book_id,))
    loan = curs.fetchall()

    if not loan:
        raise LoanNotFound
    elif only_active is True and len(loan) > 1:
        raise LoanError('Multiple active loans for book_id {}'.
                        format(book_id))

    return _serialize_loan(loan)


def add(book_id, user_id):
    '''Add a loan'''
    loan_date = datetime.now()
    db_instance = database.get()
    curs = db_instance.cursor()
    curs.execute('insert into loans'
                 '(book_id, user_id, loan_date)'
                 'VALUES (?, ?, ?)',
                 (book_id,
                  user_id,
                  int(loan_date.timestamp())))
    loan_id = curs.lastrowid
    db_instance.commit()
    return loan_id
