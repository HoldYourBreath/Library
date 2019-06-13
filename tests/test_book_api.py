import unittest
import json
import copy
import codecs

from .books.basic_book import BasicBookTestCase
from .books.example_books import book1, book2, book3, book4, \
                                 get_book, get_descriptor


class BookTestCase(BasicBookTestCase):
    def test_override_put(self):
        books = [get_book(book2, book_id=1), get_book(book1, book_id=2)]

        self.put_book(books[1])
        temp_book = copy.copy(books[0])
        temp_book['isbn'] = 5678
        temp_book['book_id'] = 3
        self.put_book(temp_book)
        temp_book = copy.copy(books[0])
        temp_book['book_id'] = 4
        self.put_book(temp_book)
        self.put_book(books[0])

        rv = self.app.get('/api/books')
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 3)

    def test_put_empty_book(self):
        self.put_book({'book_id': 1}, expected_code=400)

    def test_put_only_isbn_and_room(self):
        book = {'book_id': 1,
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

        # rv = self.app.put('/api/books/ebids/1',
        #                   data=json.dumps({'isbn': 1, 'room_id': 1}),
        #                   content_type='application/json')
        # response = codecs.decode(rv.data)
        # self.assertEqual(rv.status_code, 200)
        self.put_book({'book_id': 1, 'isbn': 1, 'room_id': 1})

        rv = self.app.get('/api/books/ebids/1')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), book)

    def test_put_invalid_id(self):
        # Try to PUT a new book with invalid id
        self.put_book({'book_id': '123jaasdasd', 'isbn': 1},
                      expected_code=400)

    def test_put_invalid_isbn(self):
        # Try to PUT a new book with invalid ISBN
        self.put_book(get_book({'isbn': 'asdasd'}), expected_code=400)

    def test_put_invalid_page_number(self):
        # Try to PUT a new book with invalid page number
        book = get_book({'isbn': '123', 'pages': '12asd21'})
        self.put_book(book, expected_code=400)

    def test_find_isbn(self):
        book = copy.deepcopy(book1)
        book['isbn'] = 9
        book_ebid = get_book(book, book_id=1)
        self.put_book(book_ebid)
        self.put_book(get_book(book1, book_id=2))
        self.put_book(get_book(book2, book_id=3))
        rv = self.app.get('/api/books/9')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), get_descriptor(book))

    @unittest.skip("Search not sypported")
    def test_find_title(self):
        self.put_book(get_book(book1))
        self.put_book(get_book(book2))
        self.put_book(get_book(book3))
        self.put_book(get_book(book4))

        # Search for title Great Book. Should get 1 book
        rv = self.app.get('/api/books?title=Great%20Songs')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], get_book(book3))

        # Search for title Great. Should get 3 books
        rv = self.app.get('/api/books?title=Great')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 3)
        self._compare_book(json.loads(response)[0], get_book(book2))
        self._compare_book(json.loads(response)[1], get_book(book3))
        self._compare_book(json.loads(response)[2], get_book(book4))

    @unittest.skip("Search not sypported")
    def test_find_description(self):
        self.put_book(get_book(book1))
        self.put_book(get_book(book2))
        self.put_book(get_book(book3))
        self.put_book(get_book(book4))

        # Search for description artists. Should get 1 book
        rv = self.app.get('/api/books?description=poets')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], get_book(book4))

        # Search for description 'All the best'. Should get 2 book
        rv = self.app.get('/api/books?description=All%20the%20best')

    @unittest.skip("Search not sypported")
    def test_find_description_and_title(self):
        self.put_book(get_book(book1))
        self.put_book(get_book(book2))
        self.put_book(get_book(book3))
        self.put_book(get_book(book4))

        # Search for title Great and description 'artists'
        # Should get 1 book
        rv = self.app.get('/api/books?title=Great&description=artists')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 1)
        self._compare_book(json.loads(response)[0], get_book(book3))

    @unittest.skip("Search not sypported")
    def test_filter_out_loaned(self):
        loaned_book = copy.copy(get_book(book1))
        loaned_book['loaned'] = True
        self.put_book(loaned_book)
        self.put_book(get_book(book2))

        self.app.put('/api/books/ebids/{}/loan'.format(loaned_book['id']),
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
        self._compare_book(json.loads(response)[0], get_book(book2))

        # Make sure a specific get will not mark book as loaned
        rv = self.app.get('/api/books/{}'.format(get_book(book2)['id']))
        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self._compare_book(json.loads(response), get_book(book2))

    @unittest.skip("Search not sypported")
    def test_find_location(self):
        self.put_book(get_book(book1))
        self.put_book(get_book(book2))
        self.put_book(get_book(book3))
        self.put_book(get_book(book4))

        # Search for title Great and description 'artists'
        # Should get 1 book
        rv = self.app.get('/api/books?room=happy%20room')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], get_book(book1))
        self._compare_book(json.loads(response)[1], get_book(book2))

        # Search for room ID 2
        rv = self.app.get('/api/books?room_id=2')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], get_book(book1))
        self._compare_book(json.loads(response)[1], get_book(book2))

        # Search for site name Happy place
        rv = self.app.get('/api/books?site=happy%20place')

        self.assertEqual(rv.status_code, 200)
        response = codecs.decode(rv.data)
        self.assertEqual(len(json.loads(response)), 2)
        self._compare_book(json.loads(response)[0], get_book(book1))
        self._compare_book(json.loads(response)[1], get_book(book2))


if __name__ == '__main__':
    unittest.main()
