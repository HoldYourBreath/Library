import os
import unittest
import tempfile
import json
import ConfigParser

# Local modules
import library.server as server
import library.database as database
import library.config as config


class ServerTestCase(unittest.TestCase):

    def setUp(self):
        # Set up a temporary database
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            database.init()

        # Set up a temporary config file
        config.config = ConfigParser.ConfigParser()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])


class RootTestCase(ServerTestCase):
    def test_root(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)




if __name__ == '__main__':
    unittest.main()
