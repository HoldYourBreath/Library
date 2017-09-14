from .test_server import ServerTestCase

import library.database as database
import library.loan as loan


class LoanTestCase(ServerTestCase):
    dummy_book_id = 1
    dummy_user_id = 2

    def setUp(self):
        ServerTestCase.setUp(self)
        book = {'tag': self.dummy_book_id,
                'isbn': 1234,
                'room_id': 1}
        self.add_book(book)

    def test_loan(self):
        with self.app.session_transaction():
            loan_id = loan.add(self.dummy_book_id,
                               self.dummy_user_id)
            test_loan = loan.get(loan_id)
            self.compare_loan(test_loan,
                              self.dummy_book_id,
                              self.dummy_user_id)

    def test_add_loan_no_book(self):
        """
        Loan a non existent book

        Loaning a non existent book should not be allowed
        """
        with self.app.session_transaction():
            with self.assertRaises(loan.LoanNotAllowed):
                loan.add(self.dummy_book_id + 1000,
                         self.dummy_user_id)

    def test_loan_all(self):
        with self.app.session_transaction():
            num_loans = 42
            loans = {}
            for book_id in range(2, num_loans+1):
                book = {'tag': book_id,
                        'isbn': 1234,
                        'room_id': 1}
                self.add_book(book)

            for book_id in range(1, num_loans+1):
                loan_id = loan.add(book_id,
                                   self.dummy_user_id)
                loans[loan_id] = book_id

            self.assertEqual(num_loans, len(loan.get_all()))
            for test_loan in loan.get_all():
                book_id = loans[test_loan['id']]
                self.compare_loan(test_loan,
                                  book_id,
                                  self.dummy_user_id)

    def test_get_by_book_id(self):
        with self.app.session_transaction():
            loan_id1 = loan.add(self.dummy_book_id,
                                self.dummy_user_id)
            test_loan = loan.by_book_id(self.dummy_book_id)
            self.assertEqual(test_loan['id'], loan_id1)
            self.assertIsNone(test_loan['return_date'])
            self.compare_loan(test_loan,
                              self.dummy_book_id,
                              self.dummy_user_id)

            # Add a second one and fetch that using book_id
            loan.remove(loan_id1)
            loan_id2 = loan.add(self.dummy_book_id,
                                self.dummy_user_id)
            test_loan = loan.by_book_id(self.dummy_book_id)
            self.assertEqual(test_loan['id'], loan_id2)
            self.assertIsNone(test_loan['return_date'])
            self.compare_loan(test_loan,
                              self.dummy_book_id,
                              self.dummy_user_id)

            loans = loan.by_book_id(self.dummy_book_id,
                                    only_active=False)
            loans_dict = {loan['id']: loan for loan in loans}

            # Loan 1 should be returned
            test_loan = loans_dict[loan_id1]
            self.assertEqual(test_loan['id'], loan_id1)
            self.assertIsNotNone(test_loan['return_date'])
            self.compare_loan(test_loan,
                              self.dummy_book_id,
                              self.dummy_user_id)

            # Loan 2 should be active
            test_loan = loans_dict[loan_id2]
            self.assertEqual(test_loan['id'], loan_id2)
            self.assertIsNone(test_loan['return_date'])
            self.compare_loan(test_loan,
                              self.dummy_book_id,
                              self.dummy_user_id)

    def test_no_loan(self):
        with self.app.session_transaction():
            test_loan_id = loan.add(self.dummy_book_id,
                                    self.dummy_user_id)
            with self.assertRaises(loan.LoanNotFound):
                loan.get(test_loan_id + 10)

            with self.assertRaises(loan.LoanNotFound):
                loan.by_book_id(self.dummy_book_id + 10)

    def test_remove(self):
        with self.app.session_transaction():
            loan_id = loan.add(self.dummy_book_id,
                               self.dummy_user_id)

            # Loan should be active
            test_loan = loan.get(loan_id)
            self.assertIsNone(test_loan['return_date'])

            # Return loan by id
            loan.remove(loan_id)

            # Loan should be returned
            test_loan = loan.get(loan_id)
            self.assertIsNotNone(test_loan['return_date'])

            loan_id = loan.add(self.dummy_book_id,
                               self.dummy_user_id)

            # Loan should be active
            test_loan = loan.by_book_id(self.dummy_book_id)
            self.assertIsNone(test_loan['return_date'])

            # Return loan for dummy_book
            loan.remove_on_book(self.dummy_book_id)

            # Loan should be returned
            test_loan = loan.get(loan_id)
            self.assertIsNotNone(test_loan['return_date'])

    def test_remove_returned_book(self):
        with self.app.session_transaction():
            loan_id = loan.add(self.dummy_book_id,
                               self.dummy_user_id)

            loan.remove(loan_id)
            with self.assertRaises(loan.LoanNotFound):
                loan.remove(loan_id)

            loan_id = loan.add(self.dummy_book_id,
                               self.dummy_user_id)

            # Return loan for dummy_book
            loan.remove_on_book(self.dummy_book_id)
            with self.assertRaises(loan.LoanNotFound):
                loan.remove_on_book(self.dummy_book_id)

    def test_add_multiple_loans_same_book(self):
        with self.app.session_transaction():
            loan.add(self.dummy_book_id,
                     self.dummy_user_id)
            with self.assertRaises(loan.LoanNotAllowed):
                loan.add(self.dummy_book_id,
                         self.dummy_user_id)

            # Test error state, too many active loans
            db = database.get()
            for _ in range(3):
                # Insert three active loans
                db.execute('INSERT INTO loans '
                           '(book_id, user_id, loan_date) '
                           'VALUES (?, ?, 1234)',
                           (self.dummy_book_id,
                            self.dummy_user_id))

            with self.assertRaises(loan.LoanError):
                # Loan error due to too many active loans for book
                loan.by_book_id(self.dummy_book_id)

    def compare_loan(self, in_loan, book_id, user_id):
        self.assertEqual(in_loan['book_id'], book_id)
        self.assertEqual(in_loan['user_id'], user_id)
