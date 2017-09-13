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
        site_id = self.add_site('DefaultSite')
        self.add_room(site_id, 'DefaltRoom')

    def add_book(self, book):
        book_id = book['tag']
        temp_book = copy.copy(book)
        del temp_book['tag']
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


if __name__ == '__main__':
    unittest.main()
