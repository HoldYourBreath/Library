import unittest
import json
import copy
import codecs
from ldap3.core.exceptions import LDAPBindError

from .test_server import ServerTestCase
import library.server as server


class SessionTestCase(ServerTestCase):
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
