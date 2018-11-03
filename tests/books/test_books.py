import unittest
import json
import codecs
import copy

from tests.books.basic_book import BasicBookTestCase
from tests.books.example_books import book1, book2, book3, book4


class BookTestCase(BasicBookTestCase):
    def test_books_get(self):
        rv = self.app.get('/api/books/ebids')
        self.assertEqual(rv.status_code, 200)

    def test_book_get_unknown(self):
        rv = self.app.get('/api/books/ebids/1')
        self.assertEqual(rv.status_code, 404)

    def test_book_put(self):
        books = [book1]
        self._put_book(books[0])

        rv = self.app.get('/api/books/ebids/{}'.format(books[0]['book_id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self._compare_book(response[0], books[0])

    def _put_book(self, book):
        book_id = book['book_id']
        temp_book = copy.copy(book)
        del temp_book['book_id']
        url = "/api/books/ebids/{}".format(book_id)
        return super()._put_book(temp_book, url)


if __name__ == '__main__':
    unittest.main()
