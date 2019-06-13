import json
import copy

from tests.test_server import ServerTestCase


class BasicBookTestCase(ServerTestCase):
    def setUp(self):
        super().setUp()
        # Create some rooms
        site_id = self.add_site('happy place')
        self.add_room(site_id, 'happy room')

        site_id = self.add_site('testing')
        for name in '3456':
            self.add_room(site_id, name)

    def tearDown(self):
        self.remove_admin('admin')
        super().tearDown()

    def put_book(self, book, expected_code=200):
        book_id = book['book_id']
        temp_book = copy.copy(book)
        del temp_book['book_id']
        url = "/api/books/ebids/{}".format(book_id)
        return self._put_book(temp_book, url, expected_code)

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

    def _put_book(self, book, url, expected_code=200):
        self.create_session(user=self.ADMIN, update_session=True)
        rv = self.app.put(url,
                          data=json.dumps(book),
                          content_type='application/json')
        self.assertEqual(rv.status_code, expected_code)
        self.delete_session()
        return rv
