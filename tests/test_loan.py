from .test_server import ServerTestCase

import library.loan as loan


class LoanTestCase(ServerTestCase):
    dummy_book_id = 1
    dummy_user_id = 2

    def test_book(self):
        with self.app.session_transaction():
            test_loan_id = loan.add(self.dummy_book_id,
                                    self.dummy_user_id)
            test_loan = loan.get(test_loan_id)
            self.assertEqual(test_loan['book_id'],
                             self.dummy_book_id)
            self.assertEqual(test_loan['user_id'],
                             self.dummy_user_id)

    def test_no_loan(self):
        with self.app.session_transaction():
            test_loan_id = loan.add(self.dummy_book_id,
                                    self.dummy_user_id)
            with self.assertRaises(loan.LoanNotFound):
                test_loan = loan.get(test_loan_id + 10)
