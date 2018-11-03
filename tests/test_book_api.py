import unittest
import json
import copy
import codecs

from .books.basic_book import BasicBookTestCase
from .books.example_books import book1, book2, book3, book4


class BookTestCase(BasicBookTestCase):
    def test_books_get(self):
        rv = self.app.get('/api/books')
        self.assertEqual(rv.status_code, 200)

    def test_book_get_unknown(self):
        rv = self.app.get('/api/books/1')
        self.assertEqual(rv.status_code, 404)

    def test_book_put(self):
        books = [book1]
        self.add_book(books[0])

        rv = self.app.get('/api/books/{}'.format(books[0]['id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        rv = self.app.get('/api/books')
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self._compare_book(response[0], books[0])

    def test_delete_room_books_in_room(self):
        room_name = 'Reading'
        site_id = self.add_site('test')
        room_id = self.add_room(site_id, room_name)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 200)
        books = [book1]
        self._put_book(books[0])
        rv = self.app.get('/api/books/{}'.format(books[0]['id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])
        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response)[0], books[0])
        test_book = copy.copy(book2)
        test_book['room_id'] = room_id
        self._put_book(test_book)
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
        books = [book2, book1]
        self._put_book(books[1])
        self._put_book(books[0])

        rv = self.app.get('/api/books/{}'.format(books[1]['id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[1])

        rv = self.app.get('/api/books/{}'.format(books[0]['id']))
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), books[0])

        # Test adding another copy of an existing book
        same_book = copy.copy(book1)
        same_book['id'] = 3
        self._put_book(same_book)

        rv = self.app.get('/api/books/{}'.format(same_book['id']))
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
        book = {'id': 1,
                'isbn': 1,
                'title': '',
                'room_id': 1,
                'authors': [],
                'pages': 0,
                'format': '',
                'publisher': '',
                'publication_date': '',
                'description': '',
                'thumbnail': '',
                'loaned': False}

        rv = self.app.put('/api/books/1',
                          data=json.dumps({'isbn': 1, 'room_id': 1}),
                          content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        self._compare_book(json.loads(response), book)

    def test_put_invalid_id(self):
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

    def test_find_isbn(self):
        book = copy.deepcopy(book1)
        book['id'] = 12345
        book['isbn'] = 9
        self._put_book(book)
        self._put_book(book1)
        self._put_book(book2)
        rv = self.app.get('/api/books?isbn=9')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], book)

    def test_find_title(self):
        self._put_book(book1)
        self._put_book(book2)
        self._put_book(book3)
        self._put_book(book4)

        # Search for title Great Book. Should get 1 book
        rv = self.app.get('/api/books?title=Great%20Songs')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], book3)

        # Search for title Great. Should get 3 books
        rv = self.app.get('/api/books?title=Great')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 3)
        self._compare_book(json.loads(response)[0], book2)
        self._compare_book(json.loads(response)[1], book3)
        self._compare_book(json.loads(response)[2], book4)

    def test_find_description(self):
        self._put_book(book1)
        self._put_book(book2)
        self._put_book(book3)
        self._put_book(book4)

        # Search for description artists. Should get 1 book
        rv = self.app.get('/api/books?description=poets')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], book4)

        # Search for description 'All the best'. Should get 2 book
        rv = self.app.get('/api/books?description=All%20the%20best')

    def test_find_description_and_title(self):
        self._put_book(book1)
        self._put_book(book2)
        self._put_book(book3)
        self._put_book(book4)

        # Search for title Great and description 'artists'
        # Should get 1 book
        rv = self.app.get('/api/books?title=Great&description=artists')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], book3)

    def test_get_returned_book(self):
        self._put_book(book1)
        self.app.put('/api/books/{}/loan'.format(book1['id']),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/{}/loan'.format(book1['id']))
        rv = self.app.get('/api/books/{}'.format(book1['id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), book1)

    def test_get_multiple_returned_book(self):
        self._put_book(book1)
        self.app.put('/api/books/{}/loan'.format(book1['id']),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/{}/loan'.format(book1['id']))
        self.app.put('/api/books/{}/loan'.format(book1['id']),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/{}/loan'.format(book1['id']))
        self.app.put('/api/books/{}/loan'.format(book1['id']),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        self.app.delete('/api/books/{}/loan'.format(book1['id']))
        rv = self.app.get('/api/books/{}'.format(book1['id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), book1)

        # Loan book again and make sure it's marked as loaned
        self.app.put('/api/books/{}/loan'.format(book1['id']),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')
        rv = self.app.get('/api/books/{}'.format(book1['id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)

        loaned_book = copy.copy(book1)
        loaned_book['loaned'] = True
        self._compare_book(json.loads(response), loaned_book)

    def test_filter_out_loaned(self):
        loaned_book = copy.copy(book1)
        loaned_book['loaned'] = True
        self._put_book(loaned_book)
        self._put_book(book2)

        self.app.put('/api/books/{}/loan'.format(loaned_book['id']),
                     data=json.dumps({'user_id': 'test_user'}),
                     content_type='application/json')

        # Book 1 is loaned so return only that one
        rv = self.app.get('/api/books?loaned=true')
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], loaned_book)

        # Make sure a specific get will mark book as loaned
        rv = self.app.get('/api/books/{}'.format(loaned_book['id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), loaned_book)

        # Book 1 is loaned so only book2 should be returned
        rv = self.app.get('/api/books?loaned=false')
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], book2)

        # Make sure a specific get will not mark book as loaned
        rv = self.app.get('/api/books/{}'.format(book2['id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), book2)

    def test_find_location(self):
        self._put_book(book1)
        self._put_book(book2)
        self._put_book(book3)
        self._put_book(book4)

        # Search for title Great and description 'artists'
        # Should get 1 book
        rv = self.app.get('/api/books?room=happy%20room')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], book1)
        self._compare_book(json.loads(response)[1], book2)

        # Search for room ID 2
        rv = self.app.get('/api/books?room_id=2')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], book1)
        self._compare_book(json.loads(response)[1], book2)

        # Search for site name Happy place
        rv = self.app.get('/api/books?site=happy%20place')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], book1)
        self._compare_book(json.loads(response)[1], book2)

    def test_loan_book(self):
        # Fetch loan for non existing book should return 404
        rv = self.app.get('/api/books/123456/loan')
        self.assertEqual(rv.status_code, 404)

        # Loan request to non existing book should return 404
        rv = self.app.put('/api/books/123456/loan',
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 404)

        book_id = book1['id']
        self._put_book(book1)

        # Fetch loan for book without loan should return 404
        rv = self.app.get('/api/books/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 404)

        # Loan book
        rv = self.app.put('/api/books/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # Multiple loans should not be allowed
        rv = self.app.put('/api/books/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 2}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 403)

        # Fetch loan for book
        rv = self.app.get('/api/books/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(json.loads(response)['book_id'], book_id)

    def test_loan_book_malformed_request(self):
        book_id = book1['id']
        self._put_book(book1)

        # Empty loan request should yield 400
        rv = self.app.put('/api/books/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 400)

        # Loan book
        rv = self.app.put('/api/books/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # Loan request without user_id should yield 400
        rv = self.app.put('/api/books/{}/loan'.format(book_id),
                          data=json.dumps({}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_return_book(self):
        # Return loan on unknown book
        rv = self.app.delete('/api/books/1234/loan')
        self.assertEqual(rv.status_code, 404)

        book_id = book1['id']
        self._put_book(book1)

        # Return unloaned book should yield 404
        rv = self.app.delete('/api/books/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 404)

        # Loan book
        rv = self.app.put('/api/books/{}/loan'.format(book_id),
                          data=json.dumps({'user_id': 1}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

        # Return book
        rv = self.app.delete('/api/books/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(json.loads(response)['book_id'], book_id)
        self.assertIsNotNone(json.loads(response)['return_date'])

        # Return unloaned book should yield 404
        rv = self.app.delete('/api/books/{}/loan'.format(book_id))
        self.assertEqual(rv.status_code, 404)

    def _get_loans(self):
        rv = self.app.get('/api/loans',
                          content_type='application/json')
        response = codecs.decode(rv.data)
        return json.loads(response)

    def _loan_book(self, book_id, employee_num):
        return self.app.put('/api/loan/{}'.format(book_id),
                            data=json.dumps({'employee_num': employee_num}),
                            content_type='application/json')

    def _compare_book(self, lv, rv):
        # Test that lv and rv has the same size
        lvs = set(lv.keys())
        rvs = set(rv.keys())
        diff = rvs - lvs
        if diff:
            print(diff)
        diff = lvs - rvs
        if diff:
            print(diff)

        self.assertEqual(len(lv.keys()), len(rv.keys()))

        # Compare rv and lv
        for key in rv.keys():
            self.assertEqual(lv[key], rv[key])



if __name__ == '__main__':
    unittest.main()
