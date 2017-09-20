import json
import codecs

from .test_server import ServerTestCase


class LoanApiTestCase(ServerTestCase):
    dummy_book_id = 1
    dummy_user_id = 200

    def setUp(self):
        ServerTestCase.setUp(self)
        book = {'id': self.dummy_book_id,
                'isbn': 1234,
                'room_id': 1}
        self.add_admin('admin')
        self.create_session(user='admin', update_session=True)
        self.add_book(book)

    def tearDown(self):
        self.remove_admin('admin')
        ServerTestCase.tearDown(self)

    def test_loans(self):
        rv = self.app.get('/api/loans')
        response = json.loads(codecs.decode(rv.data))

        self.assertEqual(response, [])

        loan_id = self.add_loan(self.dummy_book_id,
                                self.dummy_user_id)

        # Check that the loan exist with expected parameters
        rv = self.app.get('/api/loans')
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        response = response[0]
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response['book_id'], self.dummy_book_id)
        self.assertEqual(response['user_id'], self.dummy_user_id)
        self.assertIsNotNone(response['loan_date'])
        self.assertIsNone(response['return_date'])

        test_loan = self.get_loan(loan_id)
        self.assertEqual(test_loan['book_id'], self.dummy_book_id)
        self.assertEqual(test_loan['user_id'], self.dummy_user_id)
        self.assertIsNotNone(test_loan['loan_date'])
        self.assertIsNone(test_loan['return_date'])

    def test_delete_loan(self):
        loan_id = self.add_loan(self.dummy_book_id,
                                self.dummy_user_id)

        rv = self.app.delete('/api/loans/{}'.format(loan_id))
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response['book_id'], self.dummy_book_id)
        self.assertEqual(response['user_id'], self.dummy_user_id)
        self.assertIsNotNone(response['loan_date'])
        self.assertIsNotNone(response['return_date'])

        test_loan = self.get_loan(loan_id)
        self.assertEqual(test_loan['book_id'], self.dummy_book_id)
        self.assertEqual(test_loan['user_id'], self.dummy_user_id)
        self.assertIsNotNone(test_loan['loan_date'])
        self.assertIsNotNone(test_loan['return_date'])

    def test_add_loan_malformed_request(self):
        # No content
        rv = self.app.post('/api/loans')
        self.assertEqual(rv.status_code, 400)

        # Only book_id
        rv = self.app.post('/api/loans',
                           data=json.dumps({'book_id': self.dummy_book_id}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 400)

        # Only user_id
        rv = self.app.post('/api/loans',
                           data=json.dumps({'user_id': self.dummy_user_id}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def add_loan(self, book_id, user_id):
        rv = self.app.post('/api/loans',
                           data=json.dumps({'book_id': book_id,
                                            'user_id': user_id}),
                           content_type='application/json')

        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response['book_id'], book_id)
        self.assertEqual(response['user_id'], user_id)
        self.assertIsNotNone(response['loan_date'])
        self.assertIsNone(response['return_date'])

        return response['id']

    def get_loan(self, loan_id):
        rv = self.app.get('/api/loans/{}'.format(loan_id))
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        return response
