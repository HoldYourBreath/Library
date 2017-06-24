import flask
from ldap3.core.exceptions import LDAPBindError

from .test_server import ServerTestCase
from library.app import app
import json
import codecs
import library.session as session

TEST_SIGNUM = "book_reader"


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

    def _create_session(self) -> str:
        """
        Creates a session.

        :return: Session secret
        """
        rv = self.app.post('/api/login',
                           data=json.dumps({'signum': TEST_SIGNUM,
                                            'password': 'page4'}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        secret = json.loads(response)['secret']
        self.assertTrue(secret)
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
