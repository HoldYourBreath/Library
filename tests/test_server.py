import os
import json
import copy
import unittest
import tempfile
import configparser
import codecs

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
    ADMIN = "admin"

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
        self.add_admin(self.ADMIN)
        site_id = self.add_site('DefaultSite')
        self.add_room(site_id, 'DefaltRoom')

    def add_book(self, book):
        book_id = book['id']
        temp_book = copy.copy(book)
        del temp_book['id']
        rv = self.app.put('/api/books/ebids/{}'.format(book_id),
                          data=json.dumps(temp_book),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def add_site(self, name):
        self.create_session(user=self.ADMIN, update_session=True)
        rv = self.app.post('/api/sites',
                           data=json.dumps({'name': name}),
                           content_type='application/json')

        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.delete_session()
        return response['id']

    def add_room(self, site_id, name):
        self.create_session(user=self.ADMIN, update_session=True)
        rv = self.app.post('/api/sites/{}/rooms'.format(site_id),
                           data=json.dumps({'name': name}),
                           content_type='application/json')

        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.delete_session()
        return response['id']

    def remove_room(self, site_id, name):
        self.create_session(user=self.ADMIN, update_session=True)
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, name))
        self.assertEqual(rv.status_code, 200)
        self.delete_session()

    def remove_room_not_found(self, site_id, name):
        self.create_session(user=self.ADMIN, update_session=True)
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, name))
        self.assertEqual(rv.status_code, 404)
        self.delete_session()

    def remove_room_fail(self, site_id, name):
        self.create_session(user=self.ADMIN, update_session=True)
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, name))
        self.assertEqual(rv.status_code, 403)
        self.delete_session()

    def tearDown(self):
        self.remove_admin(self.ADMIN)
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

        class UserSession:
            def __init__(self, session_id, secret):
                self.id = session_id
                self.secret = secret

        if not user:
            user = self.TEST_SIGNUM

        rv = self.app.post('/api/login',
                           data=json.dumps({'user': user,
                                            'password': password}),
                           content_type='application/json')
        response = codecs.decode(rv.data)
        self.assertEqual(rv.status_code, 200)
        session_id = json.loads(response)['session_id']
        secret = json.loads(response)['session_secret']
        self.assertTrue(secret)

        if update_session:
            with self.app.session_transaction() as sess:
                sess['session_id'] = session_id
                sess['session_secret'] = secret

        return UserSession(session_id, secret)

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
            del sess['session_id']
            del sess['session_secret']


if __name__ == '__main__':
    unittest.main()
