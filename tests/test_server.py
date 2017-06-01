import os
import json
import unittest
import tempfile
import configparser
from ldap3.core.exceptions import LDAPBindError

# Local modules
import library.server as server
import library.database as database
import library.config as config


class ServerTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        # Set up a temporary database
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            database.init()

        # Set up a temporary config file
        config.config = configparser.ConfigParser()
        self._post_new_site()

    def _post_new_site(self):
        rv = self.app.post('/api/sites',
                           data=json.dumps({"name": "DefaultSite"}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def _post_new_room(self):
        rv = self.app.post(
            '/api/rooms',
            data=json.dumps({"name": "DefaultRoom", "site_id": 1}),
            content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])


class RootTestCase(ServerTestCase):
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
        server.ldap = self.ldap_stub

    def test_root(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_add_book(self):
        rv = self.app.get('/add_book')
        self.assertEqual(rv.status_code, 200)

    def test_add_delete_db(self):
        rv = self.app.get('/delete_db')
        self.assertEqual(rv.status_code, 200)

    def test_add_init_db(self):
        rv = self.app.get('/init_db')
        self.assertEqual(rv.status_code, 200)

    def test_login(self):
        rv = self.app.get('/login')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/login', data=dict(
            signum='test',
            password='testpass'))

        self.assertEqual(self.ldap_stub.user, 'test')
        self.assertEqual(self.ldap_stub.password, 'testpass')

        # Make sure we are redirected
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 'http://localhost/')

    def test_login_fail(self):
        self.ldap_stub.return_value = False
        rv = self.app.post('/login', data=dict(
            signum='test',
            password='testpass'))

        self.assertEqual(self.ldap_stub.user, 'test')
        self.assertEqual(self.ldap_stub.password, 'testpass')
        self.assertEqual(rv.status_code, 200)

    def test_login_fatal(self):
        self.ldap_stub.raise_error = LDAPBindError
        with self.assertRaises(LDAPBindError):
            rv = self.app.post('/login', data=dict(
                signum='test',
                password='testpass'))


if __name__ == '__main__':
    unittest.main()
