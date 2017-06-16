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

        # Test adding another copy of an existing book
        same_book = copy.copy(book1)
        same_book['tag'] = 3
        self._put_book(same_book)

        rv = self.app.get('/api/books/3')
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), same_book)

        # Test that the number of unique books are 2, not 3.
        # Multiple books of same kind of book should not be listed
        # more than once
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

    def test_find_isbn(self):
        book = copy.deepcopy(book1)
        book['tag'] = 12345
        book['isbn'] = 9
        self._put_book(book)
        self._put_book(book1)
        self._put_book(book2)
        rv = self.app.get('/api/books?isbn=9')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], book)

    def test_find_title_and_description(self):
        great_book1 = copy.deepcopy(book1)
        great_book1['tag'] = 12345
        great_book1['isbn'] = 10
        great_book1['title'] = 'Great Songs'
        great_book1['description'] = \
            'A very nice book about songs! All the best artists'
        self._put_book(great_book1)

        # Put another book with similar title
        great_book2 = copy.deepcopy(book1)
        great_book2['tag'] = 12346
        great_book2['isbn'] = 11
        great_book2['title'] = 'Great Poems'
        great_book2['description'] = \
            'A very nice book about poems! All the best poets'
        self._put_book(great_book2)

        # Put some books for noise
        self._put_book(book1)
        self._put_book(book2)

        # Search for title Great Book. Should get 1 book
        rv = self.app.get('/api/books?title=Great%20Songs')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], great_book1)

        # Search for title Great. Should get 3 books
        rv = self.app.get('/api/books?title=Great')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 3)
        self._compare_book(json.loads(response)[0], great_book1)
        self._compare_book(json.loads(response)[1], great_book2)

        # Search for description artists. Should get 1 book
        rv = self.app.get('/api/books?description=poets')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], great_book2)

        # Search for description 'All the best'. Should get 2 book
        rv = self.app.get('/api/books?description=All%20the%20best')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], great_book1)
        self._compare_book(json.loads(response)[1], great_book2)

        # Search for title Great and description 'artists'
        # Should get 1 book
        rv = self.app.get('/api/books?title=Great&description=artists')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], great_book1)

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
        # Test that lv and rv has the same size
        self.assertEqual(len(lv.keys()), len(rv.keys()))

        # Compare rv and lv
        for key in lv.keys():
            self.assertEqual(lv[key], rv[key])


if __name__ == '__main__':
    unittest.main()
