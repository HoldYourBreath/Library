import importlib
from ldap3.core.exceptions import LDAPBindError

from .test_server import ServerTestCase
import library.config as config
import library.ldap


class MalformedDn(Exception):
    pass


class LdapTestCase(ServerTestCase):
    class Ldap3Stub():
        def __init__(self):
            self.server = ''
            self.port = 0
            self.dn = ''
            self.password = ''
            self.exception = None
            self.error_text = ''

        def Server(self, server, **kwargs):
            self.server = server
            self.port = kwargs['port']

        def Connection(self, server, dn, password, **kwargs):
            self.dn = dn
            self.password = password
            if self.exception:
                raise self.exception(self.error_text)

            return True

        def get_user(self):
            # Find starting pos
            start_pos = self.dn.find('=')

            # Find end pos
            end_pos = self.dn.find(',')

            if start_pos == 0 or end_pos == 0:
                raise MalformedDn()

            return self.dn[start_pos+1:end_pos]

        def get_user_dn(self):
            # Find starting pos
            start_pos = self.dn.find(',')

            if start_pos == 0:
                raise MalformedDn()

            return self.dn[start_pos+1:]

        def raise_exception(self, exception, text):
            '''Set up stub to raise exception in Connection function'''

            self.exception = exception
            self.error_text = text

    def setUp(self):
        ServerTestCase.setUp(self)

        # Configure LDAP
        self.default_server = 'ldap.example.com'
        self.default_port = 636
        self.default_user_dn = 'OU=Users,DC=example,DC=com'
        config.config.add_section('ldap')
        config.config.set('ldap', 'server', self.default_server)
        config.config.set('ldap', 'port', str(self.default_port))
        config.config.set('ldap', 'user_dn', self.default_user_dn)

        # Reload the module to make sure new config takes effect
        importlib.reload(library.ldap)

        # Replace ldap3 module with a stub
        self.ldap3_stub = self.Ldap3Stub()
        library.ldap.ldap3 = self.ldap3_stub

    def test_authenticate_success(self):
        user = 'test'
        password = 'testpass'

        rv = library.ldap.authenticate(user, password)

        # Authentication should be a success
        self.assertEqual(rv, True)

        # Make sure correct user and password are used against ldap
        self.assertEqual(user,
                         self.ldap3_stub.get_user())
        self.assertEqual(password, self.ldap3_stub.password)
        self.assertEqual(self.default_user_dn,
                         self.ldap3_stub.get_user_dn())
        self.assertEqual(self.default_port, self.ldap3_stub.port)
        self.assertEqual(self.default_server,
                         self.ldap3_stub.server)

    def test_authentication_failure(self):
        user = 'test'
        password = 'testpass'

        # Set up ldap stub to raise exception indicating auth fail
        self.ldap3_stub.raise_exception(LDAPBindError,
                                        'blabla invalidCredentials sdd')

        rv = library.ldap.authenticate(user, password)

        # Authentication should be a failure
        self.assertEqual(rv, False)

    def test_authentication_fatal(self):
        user = 'test'
        password = 'testpass'

        # Set up ldap stub to raise exception indicating other fault
        self.ldap3_stub.raise_exception(LDAPBindError,
                                        'some unexpected error')

        with self.assertRaises(LDAPBindError):
            rv = library.ldap.authenticate(user, password)

        # Set up ldap stub to raise an unexpected exception
        self.ldap3_stub.raise_exception(Exception,
                                        'some unexpected error')

        with self.assertRaises(Exception):
            rv = library.ldap.authenticate(user, password)
