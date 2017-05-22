import unittest
import json

from test_server import ServerTestCase


class BookTestCase(ServerTestCase):
    def test_book_get(self):
        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)

    def test_book_get_unknown(self):
        rv = self.app.get('/api/books/1')
        self.assertEqual(rv.status_code, 404)

    def test_book_put(self):
        books = [{'tag': 1,
                  'isbn': 1234}]
        self._put_book(books[0])
        rv = self.app.get('/api/books')
        self.assertEqual(rv.data, json.dumps(books))

        rv = self.app.get('/api/books/1')
        self.assertEqual(rv.data, json.dumps(books[0]))

    def test_multiple_put(self):
        books = [{'tag': 2,
                  'isbn': 5678},
                 {'tag': 1,
                  'isbn': 1234}]
        self._put_book(books[1])
        self._put_book(books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(rv.data, json.dumps(books))

        rv = self.app.get('/api/books/1')
        self.assertEqual(rv.data, json.dumps(books[1]))

        rv = self.app.get('/api/books/2')
        self.assertEqual(rv.data, json.dumps(books[0]))

    def test_override_put(self):
        books = [{'tag': 2,
                  'isbn': 2345},
                 {'tag': 1,
                  'isbn': 1234}]
        self._put_book(books[1])
        self._put_book({'tag': 2, 'isbn': 5678})
        self._put_book(books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(rv.data, json.dumps(books))

    def _put_book(self, book):
        book_id = book['tag']
        isbn = book['isbn']
        rv = self.app.put('/api/books/{}'.format(book_id), data={'isbn': isbn})
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
