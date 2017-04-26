import unittest

# Local modules
import library.server as server


class ServerTestCase(unittest.TestCase):

    @classmethod
    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    @classmethod
    def tearDown(self):
        pass

    def test_root(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_book_post(self):
        rv = self.app.post('/books', data={'isbn': 1234})
        self.assertEqual(rv.status_code, 200)
        rv = self.app.get('/books')
        self.assertEqual(rv.data, '1234')
        rv = self.app.post('/books', data={'isbn': 5678})
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/books')
        self.assertEqual(rv.data, '1234 5678')

    def test_book_get(self):
        rv = self.app.get('/books')
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
