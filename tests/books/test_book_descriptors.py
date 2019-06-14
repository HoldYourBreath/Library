import unittest
import json
import codecs

from tests.books.basic_book import BasicBookTestCase
from tests.books.example_books import book1, get_descriptor


class BookDescriptorTestCase(BasicBookTestCase):
    def test_books_get(self):
        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)

    def test_book_get_unknown(self):
        rv = self.app.get('/api/books/1')
        self.assertEqual(rv.status_code, 404)

    def test_book_put(self):
        books = [book1]

        # Creating book descriptors as non admin should not be allowed
        self._put_book(books[0], expected_code=401, create_session=False)

        self._put_book(books[0])

        rv = self.app.get('/api/books/{}'.format(books[0]['isbn']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response),
                           get_descriptor(books[0], num_copies=0))

        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self._compare_book(response[0],
                           get_descriptor(books[0], num_copies=0))

    def test_book_multiple_put(self):
        books = [book1]

        self._put_book(books[0])
        self._put_book(books[0])

        rv = self.app.get('/api/books/{}'.format(books[0]['isbn']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response),
                           get_descriptor(books[0], num_copies=0))

        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self._compare_book(response[0],
                           get_descriptor(books[0], num_copies=0))

    def _put_book(self, book, expected_code=200, create_session=True):
        isbn = book['isbn']
        url = "/api/books/{}".format(isbn)
        return super()._put_book(book, url, expected_code, create_session)


if __name__ == '__main__':
    unittest.main()
