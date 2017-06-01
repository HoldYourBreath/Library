import ldap3
from ldap3.core.exceptions import LDAPBindError
from library.config import config

SERVER = config.get('ldap', 'server')
PORT = int(config.get('ldap', 'port'))
USER_DN = config.get('ldap', 'user_dn')


def authenticate(user, password):
    server = ldap3.Server(SERVER, port=PORT, use_ssl=True)
    try:
        dn = 'uid={},{}'.format(user, USER_DN)
        ldap3.Connection(server, dn, password, auto_bind=True)
    except LDAPBindError as e:
        if 'invalidCredentials' not in e.args[0]:
            raise e
        return False

    return True
