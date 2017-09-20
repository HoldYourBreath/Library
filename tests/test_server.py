import os
import json
import copy
import unittest
import tempfile
import configparser
import codecs
from ldap3.core.exceptions import LDAPBindError

# Local modules
import library.server as server
import library.database as database
import library.config as config
import library.session as session

session.AUTHENTICATE = False


class ServerTestCase(unittest.TestCase):
    """
    """
    TEST_SIGNUM = "book_reader"

    def setUp(self):
        # Set up a temporary database
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            database.init()

        # Set up a temporary config file
        config.config = configparser.ConfigParser()

        # Add some initial sites
        self.add_admin('admin')
        self.create_session(user='admin', update_session=True)
        site_id = self.add_site('DefaultSite')
        self.add_room(site_id, 'DefaltRoom')
        self.remove_admin('admin')
        self.delete_session()

    def add_book(self, book):
        book_id = book['id']
        temp_book = copy.copy(book)
        del temp_book['id']
        rv = self.app.put('/api/books/{}'.format(book_id),
                          data=json.dumps(temp_book),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def add_site(self, name):
        rv = self.app.post('/api/sites',
                           data=json.dumps({'name': name}),
                           content_type='application/json')

        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        return response['id']

    def add_room(self, site_id, name):
        rv = self.app.post('/api/sites/{}/rooms'.format(site_id),
                           data=json.dumps({'name': name}),
                           content_type='application/json')

        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        return response['id']

    def remove_room(self, site_id, name):
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, name))
        self.assertEqual(rv.status_code, 200)

    def remove_room_not_found(self, site_id, name):
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, name))
        self.assertEqual(rv.status_code, 404)

    def remove_room_fail(self, site_id, name):
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, name))
        self.assertEqual(rv.status_code, 403)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])

    def create_session(self,
                       user=None,
                       password='dummy',
                       update_session=False) -> str:
        """
        Creates a session.

        :return: Session secret
        """
        if not user:
            user = self.TEST_SIGNUM

        rv = self.app.post('/api/login',
                           data=json.dumps({'signum': user,
                                            'password': password}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        secret = json.loads(response)['secret']
        self.assertTrue(secret)

        if update_session:
            with self.app.session_transaction() as sess:
                sess['signum'] = user
                sess['secret'] = secret

        return secret

    def add_admin(self, admin):
        with self.app.session_transaction():
            db = database.get()
            db.execute('INSERT INTO admins '
                       '(user_id, admin_level) '
                       'VALUES (?, ?)',
                       (admin, 1))
            db.commit()

    def remove_admin(self, admin):
        with self.app.session_transaction():
            db = database.get()
            db.execute('DELETE FROM admins WHERE user_id=?', (admin,))
            db.commit()

    def delete_session(self):
        with self.app.session_transaction() as sess:
            del sess['signum']
            del sess['secret']


if __name__ == '__main__':
    unittest.main()
