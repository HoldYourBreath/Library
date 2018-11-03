import unittest
import json
import copy
import codecs

from tests.test_server import ServerTestCase


class BasicBookTestCase(ServerTestCase):
    def setUp(self):
        super().setUp()
        # Create some rooms
        self.add_admin('admin')
        self.create_session(user='admin', update_session=True)

        site_id = self.add_site('happy place')
        self.add_room(site_id, 'happy room')

        site_id = self.add_site('testing')
        for name in '3456':
            self.add_room(site_id, name)

    def tearDown(self):
        self.remove_admin('admin')
        super().tearDown()

    def _compare_book(self, lv, rv):
        # Test that lv and rv has the same size
        lvs = set(lv.keys())
        rvs = set(rv.keys())
        diff = rvs - lvs
        if diff:
            print(diff)
        diff = lvs - rvs
        if diff:
            print(diff)

        self.assertEqual(len(lv.keys()), len(rv.keys()))

        # Compare rv and lv
        for key in rv.keys():
            self.assertEqual(lv[key], rv[key])

    def _put_book(self, book, url):
        rv = self.app.put(url,
                          data=json.dumps(book),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        return rv
