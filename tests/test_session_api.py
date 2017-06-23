import flask
from ldap3.core.exceptions import LDAPBindError

from .test_server import ServerTestCase
from library.app import app
import json
import codecs
import library.session as session


class SessionApiTestCase(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)

        class LdapStub:
            def __init__(self):
                self.user = None
                self.password = None
                self.return_value = True
                self.raise_error = None

            def authenticate(self, user, password):
                self.user = user
                self.password = password
                if self.raise_error:
                    raise self.raise_error()
                return self.return_value

        self.ldap_stub = LdapStub()
        session.ldap = self.ldap_stub

    def test_login(self):
        """
        Tests a simple user authentication.

        :return: None
        """
        rv = self.app.post('/api/login',
                           data=json.dumps({'signum': 'book_reader',
                                            'password': 'page4'}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(json.loads(response)['secret'])

    def test_session_update(self):
        """
        The session secret shall be updated if there already
        are a previous session for the user.

        :return: None
        """
        rv = self.app.post('/api/login',
                           data=json.dumps({'signum': 'book_reader',
                                            'password': 'page4'}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        first_secret = json.loads(response)['secret']
        self.assertEqual(rv.status_code, 200)
        rv = self.app.post('/api/login',
                           data=json.dumps({'signum': 'book_reader',
                                            'password': 'page4'}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        second_secret = json.loads(response)['secret']
        self.assertEqual(rv.status_code, 200)
        self.assertNotEqual(first_secret, second_secret)
