import os
import unittest
import tempfile
import json
import ConfigParser
from Queue import Queue, Empty

# Local modules
import library.server as server
import library.database as database
from library.config import config

class Response():
    def __init__(self, code, data):
        self.code = code
        self.data = data

class UrllibStub():

    def __init__(self, responses):
        self.responses = responses

    class Response():

        def __init__(self, code, data):
            self.code = code
            self.data = data

        def getcode(self):
            return self.code

        def read(self):
            return self.data

    def urlopen(self, url):
        try:
            response = self.responses.get(False)
        except Empty:
            raise Empty("Unexpected URL fetch. Test stub queue empty")

        return self.Response(response.code, response.data)


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        global config
        # Set up a temporary database
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            database.init()

        # Set up a temporary config file
        config = ConfigParser.ConfigParser()

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


class GoodreadsTestCase(ServerTestCase):

    def setUp(self):
        ServerTestCase.setUp(self)
        import library.goodreads_interface as gi
        self.response_queue = Queue()
        gi.urllib = UrllibStub(self.response_queue)

        config.add_section('Goodreads')
        config.set('Goodreads', 'api_key', '123456789')

        self.dir = os.path.dirname(__file__)


    def test_get_book(self):
        isbn_data = open(os.path.join(self.dir, "sample_response_isbn.xml")).read()
        book_data = open(os.path.join(self.dir, "sample_response_book_id.xml")).read()
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
                'author': ['Sandro Mancuso'],
                'title': 'The Software Craftsman: Professionalism, Pragmatism, Pride',
                'publication_date': '2014 12 04',
                'num_pages': 288,
                'description': '<b>Be a Better Developer and Deliver Better Code</b> Despite advanced tools and methodologies, software projects continue to fail. Why? Too many organizations still view software development as just another production line. Too many developers feel that way, too and they behave accordingly. In <b> <i>The Software Craftsman: Professionalism, Pragmatism, Pride, </i> </b>Sandro Mancuso offers a better and more fulfilling path. If you want to develop software with pride and professionalism; love what you do and do it with excellence; and build a career with autonomy, mastery, and purpose, it starts with the recognition that you are a craftsman. Once you embrace this powerful mindset, you can achieve unprecedented levels of technical excellence and customer satisfaction. Mancuso helped found the world s largest organization of software craftsmen; now, he shares what he s learned through inspiring examples and pragmatic advice you can use in your company, your projects, and your career. You will learn<br />Why agile processes aren t enough and why craftsmanship is crucial to making them work How craftsmanship helps you build software right and helps clients in ways that go beyond code How and when to say No and how to provide creative alternatives when you do Why bad code happens to good developers and how to stop creating and justifying it How to make working with legacy code less painful and more productive How to be pragmatic not dogmatic about your practices and tools How to lead software craftsmen and attract them to your organization What to avoid when advertising positions, interviewing candidates, and hiring developers How developers and their managers can create a true culture of learning How to drive true technical change and overcome deep patterns of skepticism <b>Sandro Mancuso</b> has coded for startups, software houses, product companies, international consultancies, and investment banks. In October 2013, he cofounded Codurance, a consultancy based on Software Craftsmanship principles and values. His involvement with Software Craftsmanship began in 2010, when he founded the London Software Craftsmanship Community (LSCC), now the world s largest and most active Software Craftsmanship community, with more than two thousand craftsmen. For the past four years, he has inspired and helped developers to organize Software Craftsmanship communities throughout Europe, the United States, and the rest of the world."'
                }

        rv = self.app.get('/api/books/goodread/1234')
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def test_multi_author(self):
        isbn_data = open(os.path.join(self.dir, "sample_response_isbn_multi_author.xml")).read()
        book_data = open(os.path.join(self.dir, "sample_response_book_id_multi_author.xml")).read()
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
                'author': ["Erik Dahlman", "Stefan Parkvall", "Johan Skold"],
                'title': '4g: Lte/Lte-Advanced for Mobile Broadband',
                'publication_date': '2013 12 20',
                'num_pages': 544,
                'description': ''
                }

        rv = self.app.get('/api/books/goodread/1234')
        response = json.loads(rv.data)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def verify_response(self, response, expected_response):
        self.assertEqual(response['author'], expected_response['author'])
        self.assertEqual(response['title'], expected_response['title'])
        self.assertEqual(response['publication_date'], expected_response['publication_date'])
        self.assertEqual(response['description'], expected_response['description'])


if __name__ == '__main__':
    unittest.main()
