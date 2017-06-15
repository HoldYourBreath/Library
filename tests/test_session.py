import flask
from ldap3.core.exceptions import LDAPBindError

from .test_server import ServerTestCase
from library.app import app
import library.session as session


class SessionTestCase(ServerTestCase):
    @classmethod
    def setUpClass(cls):
        @app.route('/testing_decorator_fail')
        @session.login_required
        def testing_decorator_fail():
            raise Exception("This should not be executed")

        @app.route('/testing_decorator_pass')
        @session.login_required
        def testing_decorator_pass():
            return 'ok'

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
        rv = self.app.get('/login')
        self.assertEqual(rv.status_code, 200)

        with app.test_client() as c:
            rv = c.post('/login', data=dict(
                signum='test',
                password='testpass'))

            self.assertEqual(self.ldap_stub.user, 'test')
            self.assertEqual(self.ldap_stub.password, 'testpass')

            self.assertIn('id', flask.session)
            self.assertIn('secret', flask.session)
            self.assertIn(flask.session['user'], 'test')

        self.verify_redirect(rv, 'http://localhost/')

    def test_login_fail(self):
        self.ldap_stub.return_value = False
        with app.test_client() as c:
            rv = c.post('/login', data=dict(
                signum='test',
                password='testpass'))

            self.assertEqual(self.ldap_stub.user, 'test')
            self.assertEqual(self.ldap_stub.password, 'testpass')
            self.assertEqual(rv.status_code, 200)

            self.assertNotIn('secret', flask.session)
            self.assertNotIn('user', flask.session)

    def test_login_fatal(self):
        self.ldap_stub.raise_error = LDAPBindError
        with self.assertRaises(LDAPBindError):
            self.app.post('/login', data=dict(
                signum='test',
                password='testpass'))

    def test_logout(self):
        with app.test_client() as c:
            c.post('/login', data=dict(
                signum='test',
                password='testpass'))
            c.get('/logout')
            self.assertNotIn('secret', flask.session)
            self.assertNotIn('user', flask.session)

    def test_login_decorator_pass(self):
        with app.test_client() as c:
            c.post('/login', data=dict(
                signum='test',
                password='testpass'))
            rv = c.get('/testing_decorator_pass')

            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data, b'ok')

    def test_login_decorator_fail(self):
        with app.test_client() as c:
            rv = c.get('/testing_decorator_fail')

            self.verify_redirect(rv, 'http://localhost/login?'
                                     'next=%2Ftesting_decorator_fail')

    def test_login_decorator_fail_wrong_user(self):
        with app.test_client() as c:
            c.post('/login', data=dict(
                signum='test',
                password='testpass'))

            # Reset session['id'] to something else
            with c.session_transaction() as sess:
                sess['id'] = '12389'

            rv = c.get('/testing_decorator_fail')

            self.verify_redirect(rv, 'http://localhost/login?'
                                     'next=%2Ftesting_decorator_fail')

    def test_login_decorator_fail_wrong_secret(self):
        with app.test_client() as c:
            c.post('/login', data=dict(
                signum='test',
                password='testpass'))

            # Reset session['id'] to something else
            with c.session_transaction() as sess:
                sess['secret'] = 'a'

            rv = c.get('/testing_decorator_fail')

            self.verify_redirect(rv, 'http://localhost/login?'
                                     'next=%2Ftesting_decorator_fail')

    def verify_redirect(self, result, location):
            # Make sure we are redirected
            self.assertEqual(result.status_code, 302)
            self.assertEqual(result.location, location)
