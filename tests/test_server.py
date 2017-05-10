import os
import unittest
import tempfile
import json

# Local modules
import library.server as server
import library.database as database


class UrllibStub():

    def __init__(self, code, data):
        self.code = code
        self.data = data

    class Response():

        def __init__(self, code, data):
            self.code = code
            self.data = data

        def getcode(self):
            return self.code

        def read(self):
            return self.data

    def urlopen(self, url):
        return self.Response(self.code, self.data)


class ServerTestCase(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            database.init()

    @classmethod
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])


class RootTestCase(ServerTestCase):
    def test_root(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)


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

class GoodreadTestCase(ServerTestCase):

    def test_get_book(self):
        import library.goodreads_interface as gi
        isbn = {'isbn': 1234}
        data = """<?xml version="1.0" encoding="UTF-8"?>
<GoodreadsResponse>
  <Request>
    <authentication>true</authentication>
      <key><![CDATA[PRIVATE]]></key>
    <method><![CDATA[search_index]]></method>
  </Request>
  <search>
  <query><![CDATA[9780134052502]]></query>
    <results-start>1</results-start>
    <results-end>1</results-end>
    <total-results>1</total-results>
    <source>Goodreads</source>
    <query-time-seconds>0.01</query-time-seconds>
    <results>
        <work>
  <id type="integer">42757860</id>
  <books_count type="integer">6</books_count>
  <ratings_count type="integer">279</ratings_count>
  <text_reviews_count type="integer">49</text_reviews_count>
  <original_publication_year type="integer">2014</original_publication_year>
  <original_publication_month type="integer">12</original_publication_month>
  <original_publication_day type="integer">3</original_publication_day>
  <average_rating>4.32</average_rating>
  <best_book type="Book">
    <id type="integer">23215733</id>
    <title>The Software Craftsman: Professionalism, Pragmatism, Pride</title>
    <author>
      <id type="integer">7127583</id>
      <name>Sandro Mancuso</name>
    </author>
    <image_url>https://images.gr-assets.com/books/1416778735m/23215733.jpg</image_url>
    <small_image_url>https://images.gr-assets.com/books/1416778735s/23215733.jpg</small_image_url>
  </best_book>
</work>

    </results>
</search>"""
        print(data)
        gi.urllib = UrllibStub(200, data)

        rv = self.app.get('/api/books/goodread/1234')
        self.assertEqual(rv.data, data)
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
