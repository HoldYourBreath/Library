from .test_server import ServerTestCase
import json
import codecs
import library.session as session
from library.app import app
import library.database as database

TEST_SIGNUM = "book_reader"


class SessionApiTestCase(ServerTestCase):
    @classmethod
    def setUpClass(cls):
        @app.route('/test_login_decorator')
        @session.login_required
        def test_login_required():
            return 'allowed'

        @app.route('/test_admin_login_decorator')
        @session.login_required(admin_required=True)
        def test_admin_login_required():
            return 'allowed'

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

    def _create_session(self) -> str:
        """
        Creates a session.

        :return: Session secret
        """
        password = 'page4'
        rv = self.app.post('/api/login',
                           data=json.dumps({'signum': TEST_SIGNUM,
                                            'password': password}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        secret = json.loads(response)['secret']
        self.assertTrue(secret)
        self.assertEqual(self.ldap_stub.user, TEST_SIGNUM)
        self.assertEqual(self.ldap_stub.password, password)
        return secret

    def test_login(self) -> None:
        """
        Tests a simple user authentication.

        :return: None
        """
        self._create_session()

    def test_session_update(self) -> None:
        """
        The session secret shall be updated if there already
        are a previous session for the user.

        :return: None
        """
        first_secret = self._create_session()
        second_secret = self._create_session()
        self.assertNotEqual(first_secret, second_secret)

    def test_validate_invalid_session(self) -> None:
        """

        :return:
        """
        rv = self.app.post('/api/login/validate',
                           data=json.dumps(
                               {'signum': TEST_SIGNUM,
                                'secret': 'this_is_an_invalid_secret_string'}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 401)

    def test_validate_valid_session(self) -> None:
        """
        Validate a session.
        :return:
        """
        secret = self._create_session()
        rv = self.app.post('/api/login/validate',
                           data=json.dumps({'signum': TEST_SIGNUM,
                                            'secret': secret}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_delete_session_using_invalid_secret(self) -> None:
        """
        The secret string is needed to delete a session. Make
        sure that it is not possible to delete a session without
        the correct secret.

        :return:
        """
        secret = self._create_session()
        rv = self.app.post('/api/login/delete',
                           data=json.dumps({'signum': TEST_SIGNUM,
                                            'secret': 'Incorrect_secret!!'}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 401)
        rv = self.app.post('/api/login/delete',
                           data=json.dumps({'signum': TEST_SIGNUM,
                                            'secret': secret}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_login_required_decorator(self):

        # Test malformed decorator usage
        with self.assertRaises(TypeError):
            @session.login_required(True)
            def test_malformed_decorator():
                pass

        self._login_decorator('/test_login_decorator')

    def test_login_admin_required_decorator(self):
        with self.app.session_transaction():
            db = database.get()
            db.execute('INSERT INTO admins '
                       '(user_id, admin_level) '
                       'VALUES(?, ?)',
                       (TEST_SIGNUM, 1))
            db.commit()

        self._login_decorator('/test_admin_login_decorator')

        # Remove the TEST_SIGNUM from admins
        with self.app.session_transaction():
            db = database.get()
            db.execute('UPDATE admins '
                       'SET user_id=? '
                       'WHERE user_id=?',
                       ('DUMMY', TEST_SIGNUM))
            db.commit()

        # TEST_SIGNUM should not longer be authorized as admin
        rv = self.app.get('/test_admin_login_decorator')
        self.assertEqual(rv.status_code, 401)

    def _login_decorator(self, route):
        # Test with no prevous login at all
        rv = self.app.get(route)
        self.assertEqual(rv.status_code, 401)

        # Test with unexisting login
        with self.app.session_transaction() as sess:
            sess['signum'] = TEST_SIGNUM
            sess['secret'] = 'wrong_one'

        rv = self.app.get(route)
        self.assertEqual(rv.status_code, 401)

        # Test with existing login
        secret = self._create_session()
        with self.app.session_transaction() as sess:
            sess['secret'] = secret

        rv = self.app.get(route)
        self.assertEqual(rv.status_code, 200)
