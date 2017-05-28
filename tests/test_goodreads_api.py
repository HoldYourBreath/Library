import os
import json
import codecs
from queue import Queue, Empty

# Local modules
from .test_server import ServerTestCase
import library.config as config


class Response():
    def __init__(self, code, data):
        self.code = code
        self.data = data


class UrllibStub():

    class Request():

        class Response():

            def __init__(self, code, data):
                self.code = code
                self.data = data

            def getcode(self):
                return self.code

            def read(self):
                return self.data

        def __init__(self, responses):
            self.responses = responses

        def urlopen(self, url):
            try:
                response = self.responses.get(False)
            except Empty:
                raise Empty("Unexpected URL fetch. Test stub queue empty")

            return self.Response(response.code, response.data)

    def __init__(self, responses):
        self.request = self.Request(responses)


class GoodreadsTestCase(ServerTestCase):

    def setUp(self):
        ServerTestCase.setUp(self)
        import library.goodreads_interface as gi
        self.response_queue = Queue()
        gi.urllib = UrllibStub(self.response_queue)

        config.config.add_section('Goodreads')
        config.config.set('Goodreads', 'api_key', '123456789')

        self.sample_dir = os.path.join(os.path.dirname(__file__),
                                       "goodreads_sample_data")

    def test_get_book(self):
        isbn_data = self.open_response("isbn.xml")
        book_data = self.open_response("book_id.xml")
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
            'author': ['Sandro Mancuso'],
            'title': 'The Software Craftsman: Professionalism, '
                     'Pragmatism, Pride',
            'publication_date': '2014 12 04',
            'num_pages': 288,
            'publisher': 'Prentice Hall',
            'format': 'Paperback',
            'description':
                '<b>Be a Better Developer and Deliv'
                'er Better Code</b> Despite advanced tools and '
                'methodologies, software projects continue to fail.'
                ' Why? Too many organizations still view software '
                'development as just another production line. Too '
                'many developers feel that way, too and they behave'
                ' accordingly. In <b> <i>The Software Craftsman: '
                'Professionalism, Pragmatism, Pride, </i> </b>Sandr'
                'o Mancuso offers a better and more fulfilling path.'
                ' If you want to develop software with pride and '
                'professionalism; love what you do and do it with '
                'excellence; and build a career with autonomy, '
                'mastery, and purpose, it starts with the recogniti'
                'on that you are a craftsman. Once you embrace this '
                'powerful mindset, you can achieve unprecedented '
                'levels of technical excellence and customer '
                'satisfaction. Mancuso helped found the world s '
                'largest organization of software craftsmen; now, '
                'he shares what he s learned through inspiring '
                'examples and pragmatic advice you can use in your '
                'company, your projects, and your career. You will '
                'learn<br />Why agile processes aren t enough and '
                'why craftsmanship is crucial to making them work '
                'How craftsmanship helps you build software right '
                'and helps clients in ways that go beyond code How'
                ' and when to say No and how to provide creative '
                'alternatives when you do Why bad code happens to '
                'good developers and how to stop creating and '
                'justifying it How to make working with legacy '
                'code less painful and more productive How to be '
                'pragmatic not dogmatic about your practices and '
                'tools How to lead software craftsmen and attract '
                'them to your organization What to avoid when '
                'advertising positions, interviewing candidates, '
                'and hiring developers How developers and their '
                'managers can create a true culture of learning '
                'How to drive true technical change and overcome '
                'deep patterns of skepticism <b>Sandro Mancuso</b> '
                'has coded for startups, software houses, product '
                'companies, international consultancies, and '
                'investment banks. In October 2013, he cofounded '
                'Codurance, a consultancy based on Software '
                'Craftsmanship principles and values. His '
                'involvement with Software Craftsmanship began in '
                '2010, when he founded the London Software '
                'Craftsmanship Community (LSCC), now the world s '
                'largest and most active Software Craftsmanship '
                'community, with more than two thousand craftsmen.'
                ' For the past four years, he has inspired and helped '
                'developers to organize Software Craftsmanship '
                'communities throughout Europe, the United States, '
                'and the rest of the world."'
                }

        rv, response = self.get_book(1234)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def test_multi_author(self):
        isbn_data = self.open_response("isbn_multi_author.xml")
        book_data = self.open_response("book_id_multi_author.xml")
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
            'author': ["Erik Dahlman", "Stefan Parkvall", "Johan Skold"],
            'title': '4g: Lte/Lte-Advanced for Mobile Broadband',
            'publication_date': '2013 12 20',
            'num_pages': 544,
            'publisher': 'Academic Press',
            'format': 'Hardcover',
            'description': ''
        }

        rv, response = self.get_book(1234)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def test_no_author(self):
        isbn_data = self.open_response("isbn_no_author.xml")
        book_data = self.open_response("book_id_no_author.xml")
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
            'author': [],
            'title': '4g: Lte/Lte-Advanced for Mobile Broadband',
            'publication_date': '2013 12 20',
            'num_pages': 544,
            'publisher': 'Academic Press',
            'format': 'Hardcover',
            'description': ''
        }

        rv, response = self.get_book(1234)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def test_no_title(self):
        isbn_data = self.open_response("isbn_no_title.xml")
        book_data = self.open_response("book_id_no_title.xml")
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
            'author': [],
            'title': '',
            'publication_date': '2013 12 20',
            'num_pages': 544,
            'publisher': 'Academic Press',
            'format': 'Hardcover',
            'description': ''
        }

        rv, response = self.get_book(1234)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def test_no_publication_date(self):
        isbn_data = self.open_response("isbn_no_publication_date.xml")
        book_data = self.open_response("book_id_no_publication_date.xml")
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
            'author': ["Erik Dahlman", "Stefan Parkvall", "Johan Skold"],
            'title': '4g: Lte/Lte-Advanced for Mobile Broadband',
            'publication_date': '',
            'publisher': 'Academic Press',
            'format': 'Hardcover',
            'num_pages': 544,
            'description': ''
        }

        rv, response = self.get_book(1234)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def test_no_page_num(self):
        isbn_data = self.open_response("isbn_no_page_num.xml")
        book_data = self.open_response("book_id_no_page_num.xml")
        self.response_queue.put(Response(200, isbn_data))
        self.response_queue.put(Response(200, book_data))

        expected_response = {
            'author': ["Erik Dahlman", "Stefan Parkvall", "Johan Skold"],
            'title': '4g: Lte/Lte-Advanced for Mobile Broadband',
            'publication_date': '',
            'num_pages': 0,
            'publisher': 'Academic Press',
            'format': 'Hardcover',
            'description': ''
        }

        rv, response = self.get_book(1234)

        self.assertEqual(rv.status_code, 200)
        self.verify_response(response, expected_response)

    def open_response(self, name):
        response = ""
        with open(os.path.join(self.sample_dir, name)) as fd:
            response = fd.read()

        return response

    def verify_response(self, lv, rv):
        test_keys = ('author', 'title', 'publication_date', 'num_pages',
                     'format', 'publisher', 'description')

        for key in test_keys:
            self.assertEqual(lv[key], rv[key])

    def get_book(self, book_id):
        rv = self.app.get('/api/books/goodreads/{}'.format(book_id))

        # Make sure to convert from bytes to UTF-8
        response = json.loads(codecs.decode(rv.data))

        return rv, response
