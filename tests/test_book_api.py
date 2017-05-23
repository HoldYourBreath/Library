import unittest
import json
import copy

from test_server import ServerTestCase

book1 = {'tag': 1,
         'isbn': 1234,
         'title': 'The book',
         'authors': ['Bob Author'],
         'description': 'a book'}

book2 = {'tag': 2,
         'isbn': 1235,
         'title': 'Great book',
         'authors': ['Jane Author'],
         'description': 'Another book'}

class BookTestCase(ServerTestCase):
    def test_book_get(self):
        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)

    def test_book_get_unknown(self):
        rv = self.app.get('/api/books/1')
        self.assertEqual(rv.status_code, 404)

    def test_book_put(self):
        books = [book1]
        self._put_book(books[0])
        rv = self.app.get('/api/books')
        self.assertEqual(rv.data, json.dumps(books))

        rv = self.app.get('/api/books/1')
        self._compare_book(json.loads(rv.data), books[0])

    def test_multiple_put(self):
        books = [book2, book1]
        self._put_book(books[1])
        self._put_book(books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(rv.data, json.dumps(books))

        rv = self.app.get('/api/books/1')
        self._compare_book(json.loads(rv.data), books[1])

        rv = self.app.get('/api/books/2')
        self._compare_book(json.loads(rv.data), books[0])

    def test_override_put(self):
        books = [book2, book1]

        self._put_book(books[1])
        temp_book = copy.copy(books[0])
        temp_book['isbn'] = 5678
        self._put_book(temp_book)
        self._put_book(books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(rv.data, json.dumps(books))

    def test_put_empty_book(self):
        rv = self.app.put('/api/books/1',
                          data=json.dumps({}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_put_only_tag(self):
        book = {'tag': 1,
                'isbn': 1,
                'title': '',
                'authors': [],
                'description': ''}

        rv = self.app.put('/api/books/1',
                          data=json.dumps({'isbn': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        self._compare_book(json.loads(rv.data), book)
        self.assertEqual(rv.data, json.dumps(book))

    def _put_book(self, book):
        book_id = book['tag']
        temp_book = copy.copy(book)
        del temp_book['tag']
        rv = self.app.put('/api/books/{}'.format(book_id),
                          data=json.dumps(temp_book),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def _compare_book(self, lv, rv):
        self.assertEqual(lv['tag'], rv['tag'])
        self.assertEqual(lv['isbn'], rv['isbn'])
        self.assertEqual(lv['authors'], rv['authors'])
        self.assertEqual(lv['description'], rv['description'])


if __name__ == '__main__':
    unittest.main()