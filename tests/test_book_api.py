import unittest
import json
import copy
import codecs

from .test_server import ServerTestCase

book1 = {'tag': 1,
         'isbn': 1234,
         'title': 'The book',
         'authors': ['Bob Author'],
         'pages': 500,
         'room_id': 1,
         'format': 'Slippery back',
         'publisher': 'Crazy dude publishing',
         'publication_date': '1820 01 02',
         'description': 'a book',
         'thumbnail': 'a thumbnail'}

book2 = {'tag': 2,
         'isbn': 1235,
         'title': 'Great book',
         'authors': ['Jane Author'],
         'pages': 123,
         'room_id': 1,
         'format': 'Sturdy thing',
         'publisher': 'Sane gal publishing',
         'publication_date': '2016 12 31',
         'description': 'Another book',
         'thumbnail': 'another thumbnail'}


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
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response)[0], books[0])

    def test_multiple_put(self):
        books = [book2, book1]
        self._put_book(books[1])
        self._put_book(books[0])

        rv = self.app.get('/api/books/1')
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[1])

        rv = self.app.get('/api/books/2')
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)

    def test_override_put(self):
        books = [book2, book1]

        self._put_book(books[1])
        temp_book = copy.copy(books[0])
        temp_book['isbn'] = 5678
        self._put_book(temp_book)
        self._put_book(books[0])

        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)

    def test_put_empty_book(self):
        rv = self.app.put('/api/books/1',
                          data=json.dumps({}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_put_only_isbn_and_room(self):
        book = {'tag': 1,
                'isbn': 1,
                'title': '',
                'room_id': 1,
                'authors': [],
                'pages': 0,
                'format': '',
                'publisher': '',
                'publication_date': '',
                'description': '',
                'thumbnail': ''}

        rv = self.app.put('/api/books/1',
                          data=json.dumps({'isbn': 1, 'room_id': 1}),
                          content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        self._compare_book(json.loads(response), book)

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

    def test_make_a_loan(self):
        """
        Make a loan for book #1 by user id 1234.
        """
        self._put_book(book1)
        rv = self.app.put('/api/loan/1',
                          data=json.dumps({'employee_num': 123}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_make_a_loan_for_non_existing_tag(self):
        """
        Make a loan for a tag that does not exist.
        """
        rv = self.app.put('/api/loan/111',
                          data=json.dumps({'employee_num': 123}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 404)

    def test_list_books_by_loan_status(self):
        """
        List all available books and all checked out books.
        """
        self._put_book(book1)
        self._put_book(book2)

        self.assertEqual(self._loan_book(1, 123).status_code, 200)
        rv = self.app.get('/api/books_on_loan',
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)

    def test_make_a_loan_and_return_book(self):
        """
        Make a loan and return the book. Check the correct
        number of books and loans.
        """
        book_tag = 1
        self._put_book(book1)
        self.assertEqual(self._loan_book(book_tag, 123).status_code, 200)

        self.assertEqual(len(self._get_loans()), 1)

        rv = self.app.delete('/api/loan/{}'.format(1),
                             content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.delete('/api/loan/{}'.format(book_tag),
                             content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        rv = self.app.delete('/api/loan/{}'.format(book_tag),
                             content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        self.assertEqual(len(self._get_loans()), 0)

        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)

    def _put_book(self, book):
        book_id = book['tag']
        temp_book = copy.copy(book)
        del temp_book['tag']
        rv = self.app.put('/api/books/{}'.format(book_id),
                          data=json.dumps(temp_book),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def _get_loans(self):
        rv = self.app.get('/api/loans',
                          content_type='application/json')
        response = codecs.decode(rv.data)
        return json.loads(response)

    def _loan_book(self, book_tag, employee_num):
        return self.app.put('/api/loan/{}'.format(book_tag),
                            data=json.dumps({'employee_num': employee_num}),
                            content_type='application/json')

    def _compare_book(self, lv, rv):
        self.assertEqual(lv['tag'], rv['tag'])
        self.assertEqual(lv['isbn'], rv['isbn'])
        self.assertEqual(lv['authors'], rv['authors'])
        self.assertEqual(lv['pages'], rv['pages'])
        self.assertEqual(lv['room_id'], rv['room_id'])
        self.assertEqual(lv['publisher'], rv['publisher'])
        self.assertEqual(lv['format'], rv['format'])
        self.assertEqual(lv['publication_date'], rv['publication_date'])
        self.assertEqual(lv['description'], rv['description'])
        self.assertEqual(lv['thumbnail'], rv['thumbnail'])


if __name__ == '__main__':
    unittest.main()
