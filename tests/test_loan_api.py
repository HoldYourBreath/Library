import json
import codecs


import library.database as database
from .test_server import ServerTestCase

import library.loan as loan


class LoanApiTestCase(ServerTestCase):
    dummy_book_id = 1
    dummy_user_id = 200

    def test_loans(self):
        rv = self.app.get('/api/loans')
        response = json.loads(codecs.decode(rv.data))

        self.assertEqual(response, [])

        rv = self.app.post('/api/loans',
                           data=json.dumps({'book_id': self.dummy_book_id,
                                            'user_id': self.dummy_user_id}),
                           content_type='application/json')

        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response['book_id'], self.dummy_book_id)
        self.assertEqual(response['user_id'], self.dummy_user_id)
        self.assertIsNotNone(response['loan_date'])
        self.assertIsNone(response['return_date'])
