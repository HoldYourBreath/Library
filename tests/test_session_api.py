from .test_server import ServerTestCase
import json
import codecs
import library.session as session
from library.app import app
import library.database as database


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


class SessionApiTestCase(ServerTestCase):
    @classmethod
    def setUpClass(cls):
        @app.route('/test_login_decorator')
        @session.login_required
        def test_login_required():
            return 'allowed'

        @app.route('/test_admin_login_decorator')
        @session.admin_required
        def test_admin_login_required():
            return 'allowed'

        # Store real ldap instance
        cls.ldap = session.ldap

    @classmethod
    def tearDownClass(cls):
        # Restore ldap instance
        session.ldap = cls.ldap

    def setUp(self):
        ServerTestCase.setUp(self)

        session.AUTHENTICATE = True
        self.ldap_stub = LdapStub()
        session.ldap = self.ldap_stub

    def tearDown(self):
        session.AUTHENTICATE = False
        ServerTestCase.tearDown(self)

    def test_login(self) -> None:
        """
        Tests a simple user authentication.

        :return: None
        """
        password = 'nameofmycat'
        self.create_session(password=password)
        self.assertEqual(self.ldap_stub.user, self.TEST_SIGNUM)
        self.assertEqual(self.ldap_stub.password, password)

    def test_login_fail(self) -> None:
        """
        Tests that non authorized users can't log in

        :return: None
        """
        self.ldap_stub.return_value = False
        rv = self.app.post('/api/login',
                           data=json.dumps({'user': self.TEST_SIGNUM,
                                            'password': 'nameofmykat'}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 401)

    def test_session_update(self) -> None:
        """
        The session secret shall be updated if there already
        are a previous session for the user.

        :return: None
        """
        first_secret = self.create_session()
        second_secret = self.create_session()
        self.assertNotEqual(first_secret, second_secret)

    def test_validate_invalid_session(self) -> None:
        """

        :return:
        """
        rv = self.app.post('/api/login/validate',
                           data=json.dumps(
                               {'session_id': self.TEST_SIGNUM,
                                'secret': 'this_is_an_invalid_secret_string'}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 401)

    def test_validate_valid_session(self) -> None:
        """
        Validate a session.
        :return:
        """
        user_session = self.create_session()
        rv = self.app.post('/api/login/validate',
                           data=json.dumps({'session_id': user_session.id,
                                            'secret': user_session.secret}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_delete_session_using_invalid_secret(self) -> None:
        """
        The secret string is needed to delete a session. Make
        sure that it is not possible to delete a session without
        the correct secret.

        :return:
        """
        user_session = self.create_session()
        rv = self.app.post('/api/login/delete',
                           data=json.dumps({'session_id': user_session.id,
                                            'secret': 'Incorrect_secret!!'}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 401)
        rv = self.app.post('/api/login/delete',
                           data=json.dumps({'session_id': user_session.id,
                                            'secret': user_session.secret}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_login_required_decorator(self):
        self._login_decorator('/test_login_decorator')

    def test_login_admin_required_decorator(self):
        self.add_admin(self.TEST_SIGNUM)
        self._login_decorator('/test_admin_login_decorator')

        # Remove the TEST_SIGNUM from admins
        self.remove_admin(self.TEST_SIGNUM)

        # TEST_SIGNUM should not longer be authorized as admin
        rv = self.app.get('/test_admin_login_decorator')
        self.assertEqual(rv.status_code, 401)

    def _login_decorator(self, route):
        # Test with no previous login at all
        rv = self.app.get(route)
        self.assertEqual(rv.status_code, 401)

        # Test with unexisting login
        with self.app.session_transaction() as sess:
            sess['session_id'] = 1234
            sess['session_secret'] = 'wrong_one'

        rv = self.app.get(route)
        self.assertEqual(rv.status_code, 401)

        # Test with existing login
        user_session = self.create_session()
        with self.app.session_transaction() as sess:
            sess['session_id'] = user_session.id
            sess['session_secret'] = user_session.secret

        rv = self.app.get(route)
        self.assertEqual(rv.status_code, 200)
