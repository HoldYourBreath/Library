import unittest
import json
import copy
import codecs

from .test_server import ServerTestCase
import library.database as database


class LocationTestCase(ServerTestCase):
    def test_get_all_locations(self):
        rv = self.app.get('/api/loc/all')
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response['sites']), 1)
        self.assertEqual(len(response['rooms']), 1)

    def test_rename_site(self):
        rv = self.app.get('/api/sites')
        response = json.loads(codecs.decode(rv.data))
        default_site_name = response[0]['site_name']
        site_id = response[0]['id']
        rv = self.app.put('/api/sites/{}'.format(site_id),
                          data=json.dumps({'name': 'newSiteName'}),
                          content_type='application/json')
        rv = self.app.get('/api/sites')
        response = json.loads(codecs.decode(rv.data))
        new_site_name = response[0]['site_name']
        self.assertNotEqual(default_site_name, new_site_name)
        self.assertEqual(rv.status_code, 200)
