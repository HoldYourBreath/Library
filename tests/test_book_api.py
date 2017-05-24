import unittest
import json
import copy

from .test_server import ServerTestCase

book1 = {'tag': 1,
         'isbn': 1234,
         'title': 'The book',
         'authors': ['Bob Author'],
         'pages': 500,
         'format': 'Slippery back',
         'publisher': 'Crazy dude publishing',
         'publication_date': '1820 01 02',
         'description': 'a book'}

book2 = {'tag': 2,
         'isbn': 1235,
         'title': 'Great book',
         'authors': ['Jane Author'],
         'pages': 123,
         'format': 'Sturdy thing',
         'publisher': 'Sane gal publishing',
         'publication_date': '2016 12 31',
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

        rv = self.app.get('/api/books/1')
        self._compare_book(json.loads(rv.data), books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(json.loads(rv.data), books)

    def test_multiple_put(self):
        books = [book2, book1]
        self._put_book(books[1])
        self._put_book(books[0])

        rv = self.app.get('/api/books/1')
        self._compare_book(json.loads(rv.data), books[1])

        rv = self.app.get('/api/books/2')
        self._compare_book(json.loads(rv.data), books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(json.loads(rv.data), books)

    def test_override_put(self):
        books = [book2, book1]

        self._put_book(books[1])
        temp_book = copy.copy(books[0])
        temp_book['isbn'] = 5678
        self._put_book(temp_book)
        self._put_book(books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(json.loads(rv.data), books)

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
                'pages': 0,
                'format': '',
                'publisher': '',
                'publication_date': '',
                'description': ''}

        rv = self.app.put('/api/books/1',
                          data=json.dumps({'isbn': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        self._compare_book(json.loads(rv.data), book)
        self.assertEqual(json.loads(rv.data), book)

    def test_put_invalid_tag(self):
        # Try to PUT a new book with invalid id
        rv = self.app.put('/api/books/123jaasdasd',
                          data=json.dumps({'isbn': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 404)

    def test_put_invalid_isbn(self):
        # Try to PUT a new book with invalid ISBN
        rv = self.app.put('/api/books/1',
                          data=json.dumps({'isbn': 'asdasd'}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_put_invalid_page_number(self):
        # Try to PUT a new book with invalid page number
        rv = self.app.put('/api/books/1',
                          data=json.dumps({'isbn': '123',
                                           'pages': '12asd21'}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)

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
        self.assertEqual(lv['pages'], rv['pages'])
        self.assertEqual(lv['publisher'], rv['publisher'])
        self.assertEqual(lv['format'], rv['format'])
        self.assertEqual(lv['publication_date'], rv['publication_date'])
        self.assertEqual(lv['description'], rv['description'])


if __name__ == '__main__':
    unittest.main()
