import os
import unittest
import tempfile

# Local modules
import library.server as server


class ServerTestCase(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            server.init_db()

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
        rv = self.app.get('/books')
        self.assertEqual(rv.status_code, 200)

    def test_book_put(self):
        self._put_book(1, 1234)
        rv = self.app.get('/books')
        self.assertEqual(rv.data, '1234')

    def test_multiple_put(self):
        self._put_book(1, 1234)
        self._put_book(2, 5678)

        rv = self.app.get('/books')
        self.assertEqual(rv.data, '5678 1234')

    def test_override_put(self):
        self._put_book(1, 1234)
        self._put_book(2, 5678)
        self._put_book(2, 2345)

        rv = self.app.get('/books')
        self.assertEqual(rv.data, '2345 1234')


    def _put_book(self, book_id, isbn):
        rv = self.app.put('/books/{}'.format(book_id), data={'isbn': isbn})
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
