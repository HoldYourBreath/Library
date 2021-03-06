from sqlite3 import IntegrityError
from datetime import datetime, timedelta

import library.database as database


class LoanError(Exception):
    pass


class LoanNotFound(Exception):
    pass


class LoanNotAllowed(Exception):
    pass


def _serialize_loan(item):
    return {
        "id": item["loan_id"],
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


def get_all():
    '''Get all loans'''
    db_instance = database.get()
    curs = db_instance.execute('select * from loans')
    loans = curs.fetchall()
    return [_serialize_loan(loan) for loan in loans]


def by_book_id(book_id, only_active=True):
    '''Get a loan by book id'''
    db_instance = database.get()
    filter_active = ''
    if only_active:
        filter_active = 'AND return_date IS NULL'
    curs = db_instance.execute('select * from loans '
                               'WHERE book_id = ? ' +
                               filter_active,
                               (book_id,))
    loans = curs.fetchall()

    if not loans:
        raise LoanNotFound
    elif only_active is True and len(loans) > 1:
        raise LoanError('Multiple active loans for book_id {}'.
                        format(book_id))

    if only_active:
        return _serialize_loan(loans[0])

    return [_serialize_loan(loan) for loan in loans]


def add(book_id, user_id):
    '''Add a loan'''
    db_instance = database.get()

    loan = db_instance.execute('SELECT * FROM loans '
                               'WHERE book_id = ? '
                               'AND return_date IS NULL',
                               (book_id,)).fetchone()

    if loan:
        # Can't have multiple active loan on one book
        raise LoanNotAllowed('Active loan detected on book {0}'.
                             format(book_id))

    loan_date = datetime.now()
    curs = db_instance.cursor()
    try:
        curs.execute('INSERT INTO loans '
                     '(book_id, user_id, loan_date) '
                     'VALUES (?, ?, ?)',
                     (book_id,
                      user_id,
                      loan_date.timestamp()))
    except IntegrityError:
        # No book with that id
        raise LoanNotAllowed

    loan_id = curs.lastrowid
    db_instance.commit()
    return loan_id


def remove(loan_id):
    db_instance = database.get()

    # Make sure loan exist and is active
    loan = get(loan_id)
    if loan['return_date'] is not None:
        # Active loan not found
        raise LoanNotFound

    return_date = datetime.now()
    curs = db_instance.cursor()
    curs.execute('UPDATE loans '
                 'SET return_date = ? '
                 'WHERE loan_id = ? ',
                 (return_date.timestamp(),
                  loan_id))
    db_instance.commit()
    return get(loan_id)


def remove_on_book(book_id):
    loan = by_book_id(book_id)
    loan_id = loan['id']

    return remove(loan_id)
