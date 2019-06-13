import unittest
import json
import codecs
import copy

from tests.books.basic_book import BasicBookTestCase
from tests.books.example_books import get_book, book1, book2


class BookTestCase(BasicBookTestCase):
    def test_books_get(self):
        rv = self.app.get('/api/books/ebids')
        self.assertEqual(rv.status_code, 200)

    def test_book_get_unknown(self):
        rv = self.app.get('/api/books/ebids/1')
        self.assertEqual(rv.status_code, 404)

    def test_book_put(self):
        books = [get_book(book1)]

        # Creating books as non admin should not be allowed
        rv = self.app.put('/api/books/ebids/1',
                          data=json.dumps(books[0]),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 401)

        self.put_book(books[0])

        rv = self.app.get('/api/books/ebids/{}'.format(books[0]['book_id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        rv = self.app.get('/api/books/ebids')
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self._compare_book(response[0], books[0])

    def test_loan_book(self):
        # Fetch loan for non existing book should return 404
        rv = self.app.get('/api/books/ebids/123456/loan')
        self.assertEqual(rv.status_code, 404)

        # Loan request to non existing book should return 404
        rv = self.app.put('/api/books/ebids/123456/loan',
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 404)

        book = get_book(book1)
        book_id = book['book_id']
        self.put_book(book)

        # Fetch loan for book without loan should return 404
        rv = self.app.get('/api/books/ebids/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 404)

        # Loan book
        rv = self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # Multiple loans should not be allowed
        rv = self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 2}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 403)

        # Fetch loan for book
        rv = self.app.get('/api/books/ebids/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(json.loads(response)['book_id'], book_id)

    def test_loan_book_malformed_request(self):
        book = get_book(book1)
        book_id = book['book_id']
        self.put_book(book)

        # Empty loan request should yield 400
        rv = self.app.put('/api/books/ebids/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 400)

        # Loan book
        rv = self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # Loan request without user_id should yield 400
        rv = self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                          data=json.dumps({}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_return_book(self):
        # Return loan on unknown book
        rv = self.app.delete('/api/books/ebids/1234/loan')
        self.assertEqual(rv.status_code, 404)

        book = get_book(book1)
        book_id = book['book_id']
        self.put_book(book)

        # Return unloaned book should yield 404
        rv = self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 404)

        # Loan book
        rv = self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # Return book
        rv = self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(json.loads(response)['book_id'], book_id)
        self.assertIsNotNone(json.loads(response)['return_date'])

        # Return unloaned book should yield 404
        rv = self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 404)

    def test_get_returned_book(self):
        book = get_book(book1)
        book_id = book['book_id']
        self.put_book(book)
        self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        rv = self.app.get('/api/books/ebids/{}'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), book)

    def test_get_multiple_returned_book(self):
        book = get_book(book1)
        book_id = book['book_id']
        self.put_book(book)
        self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/ebids/{}/loan'.format(book_id))
        rv = self.app.get('/api/books/ebids/{}'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), book)

        # Loan book again and make sure it's marked as loaned
        self.app.put('/api/books/ebids/{}/loan'.format(book_id),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        rv = self.app.get('/api/books/ebids/{}'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)

        loaned_book = copy.copy(book)
        loaned_book['loaned'] = True
        self._compare_book(json.loads(response), loaned_book)

    def test_delete_room_books_in_room(self):
        room_name = 'Reading'
        site_id = self.add_site('test')
        room_id = self.add_room(site_id, room_name)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 200)
        books = [get_book(book1)]
        book_id = books[0]['book_id']

        self.put_book(books[0])
        rv = self.app.get('/api/books/ebids/{}'.format(book_id))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])
        rv = self.app.get('/api/books/ebids')
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response)[0], books[0])
        test_book = get_book(copy.copy(book2), 2, 2)
        test_book['room_id'] = room_id
        self.put_book(test_book)
        self.remove_room_fail(site_id, room_id)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 200)

    def test_delete_room_not_found(self):
        site_id = self.add_site('test')
        room_id = 100
        self.remove_room_not_found(site_id, room_id)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 404)

    def test_multiple_put(self):
        books = [get_book(book2, 1), get_book(book1, 2, 2)]
        self.put_book(books[1])
        self.put_book(books[0])

        rv = self.app.get('/api/books/ebids/{}'.format(books[1]['book_id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[1])

        rv = self.app.get('/api/books/ebids/{}'.format(books[0]['book_id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        # Test adding another copy of an existing book
        same_book = get_book(book1, book_id=3)
        self.put_book(same_book)

        rv = self.app.get('/api/books/ebids/{}'.format(same_book['book_id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), same_book)

        # Test that the number of unique books are 2, not 3.
        # Multiple books of same kind of book should not be listed
        # more than once
        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)


if __name__ == '__main__':
    unittest.main()
