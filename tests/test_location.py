import unittest
import json
import copy
import codecs

from .test_server import ServerTestCase
import library.database as database


class SitesTestCase(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)

        # Make sure sites and rooms tables are empty
        with self.app.session_transaction():
            db = database.get()
            db.execute('DELETE FROM rooms')
            db.execute('DELETE FROM sites')
            db.commit()

        self.create_session(user='admin', update_session=True)

    def tearDown(self):
        ServerTestCase.tearDown(self)

    def test_get_sites(self):
        num_sites = 100
        for site in range(num_sites):
            self.add_site(str(site))

        rv = self.app.get('/api/sites')
        response = json.loads(codecs.decode(rv.data))
        response.sort(key=lambda site: int(site['name']))

        # Verify the number of sites returned
        self.assertEqual(len(response), num_sites)

        # Verify that all the names are correct
        for site in range(num_sites):
            self.assertEqual(response[site]['name'], str(site))

    def test_add_and_get_site(self):
        test_site_name = 'test_site'
        test_site_id = self.add_site(test_site_name)

        rv = self.app.get('/api/sites')
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['id'], test_site_id)
        self.assertEqual(response[0]['name'], test_site_name)

        rv = self.app.get('/api/sites/{}'.format(test_site_id))
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response['id'], test_site_id)
        self.assertEqual(response['name'], test_site_name)

        # Test that non admin user can't add site
        self.remove_admin('admin')
        rv = self.app.post('/api/sites',
                           data=json.dumps({'name': 'some site'}),
                           content_type='application/json')

        self.assertEqual(rv.status_code, 401)

    def test_get_invalid_site(self):
        rv = self.app.get('/api/sites/{}'.format(1000))
        self.assertEqual(rv.status_code, 404)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response['msg'], 'Site not found')

        # Non int requests should not be routed
        rv = self.app.get('/api/sites/{}'.format('notAnInt'))
        self.assertEqual(rv.status_code, 404)

    def test_add_site_invalid_request(self):
        # No data in request
        rv = self.app.post('/api/sites')
        self.assertEqual(rv.status_code, 400)

        # No name in request
        rv = self.app.post('/api/sites',
                           data=json.dumps({'something_else': 1}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_add_duplicate_site_name(self):
        """Duplicate site names should not exist"""
        self.add_site('test')
        rv = self.app.post('/api/sites',
                           data=json.dumps({'name': 'test'}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 409)

    def test_get_rooms(self):
        num_rooms = 100
        site_id = self.add_site('test')

        # No rooms should yield an empty response
        rv = self.app.get('/api/sites/{}/rooms'.format(site_id))
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response, [])

        for room in range(num_rooms):
            self.add_room(site_id, str(room))

        rv = self.app.get('/api/sites/{}/rooms'.format(site_id))
        response = json.loads(codecs.decode(rv.data))
        response.sort(key=lambda site: int(site['name']))

        # Verify the number of sites returned
        self.assertEqual(len(response), num_rooms)

        # Verify that all the names are correct
        for room in range(num_rooms):
            self.assertEqual(response[room]['name'], str(room))

    def test_get_and_add_room(self):
        site_id = self.add_site('test_site')

        test_room_name = 'room1'
        test_room_id = self.add_room(site_id, test_room_name)

        rv = self.app.get('/api/sites/{}/rooms'.format(site_id))
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['id'], test_room_id)
        self.assertEqual(response[0]['name'], test_room_name)

        rv = self.app.get(
            '/api/sites/{}/rooms/{}'.format(site_id, test_room_id))
        self.assertEqual(rv.status_code, 200)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response['id'], test_room_id)
        self.assertEqual(response['name'], test_room_name)

        # Test that non authorized user can't add rooms
        self.remove_admin('admin')
        rv = self.app.post('/api/sites/{}/rooms'.format(site_id),
                           data=json.dumps({'name': 'dummy_room'}),
                           content_type='application/json')

        self.assertEqual(rv.status_code, 401)

    def test_get_invalid_room(self):
        # Try to get room with invalid site
        rv = self.app.get('/api/sites/{}/rooms/1000'.format(1000))
        self.assertEqual(rv.status_code, 404)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response['msg'], 'Room not found')

        site_id = self.add_site('test')
        rv = self.app.get('/api/sites/{}/rooms/1000'.format(site_id))
        self.assertEqual(rv.status_code, 404)
        response = json.loads(codecs.decode(rv.data))
        self.assertEqual(response['msg'], 'Room not found')

        # Non int requests should not be routed
        rv = self.app.get('/api/sites/{}/rooms/123asd'.format(site_id))
        self.assertEqual(rv.status_code, 404)

    def test_add_room_invalid_request(self):
        site_id = self.add_site('test')
        # No data in request
        rv = self.app.post('/api/sites/{}/rooms'.format(site_id))
        self.assertEqual(rv.status_code, 400)

        # No name in request
        rv = self.app.post('/api/sites/{}/rooms'.format(site_id),
                           data=json.dumps({'something_else': 1}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_add_duplicate_room_name(self):
        room_name = 'room'

        site1 = self.add_site('test1')
        site2 = self.add_site('test2')
        self.add_room(site1, room_name)

        # Name duplication not allowed in the same site
        rv = self.app.post('/api/sites/{}/rooms'.format(site1),
                           data=json.dumps({'name': room_name}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 409)

        # Same room name can exist in muplitple sites
        self.add_room(site2, room_name)

    def test_rename_site(self):
        old_name = 'old'
        new_name = 'new'
        site_id = self.add_site(old_name)
        rv = self.app.put('/api/sites/{}'.format(site_id),
                          data=json.dumps({'name': new_name}),
                          content_type='application/json')
        rv = self.app.get('/api/sites/{}'.format(site_id))
        response = json.loads(codecs.decode(rv.data))
        new_site_name = response['name']
        self.assertEqual(new_site_name, new_name)
        self.assertEqual(rv.status_code, 200)

        # Test that non authorized user rename sites
        self.remove_admin('admin')
        rv = self.app.put('/api/sites/{}'.format(site_id),
                          data=json.dumps({'name': 'dummy_new_name'}),
                          content_type='application/json')

        self.assertEqual(rv.status_code, 401)

    def test_site_put_without_data(self):
        rv = self.app.put('/api/sites/100')
        self.assertEqual(rv.status_code, 400)

    def test_rename_room(self):
        old_name = 'old'
        new_name = 'new'
        site_id = self.add_site('test')
        room_id = self.add_room(site_id, old_name)
        rv = self.app.put('/api/sites/{}/rooms/{}'.format(site_id, room_id),
                          data=json.dumps({'name': new_name}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        response = json.loads(codecs.decode(rv.data))
        new_site_name = response['name']
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(new_site_name, new_name)

        # Test that non authorized user can't rename rooms
        self.remove_admin('admin')
        rv = self.app.put('/api/sites/{}/rooms/{}'.format(site_id, room_id),
                          data=json.dumps({'name': 'dummy_room_new_name'}),
                          content_type='application/json')

        self.assertEqual(rv.status_code, 401)

    def test_delete_room(self):
        room_name = 'Reading'
        site_id = self.add_site('test')
        room_id = self.add_room(site_id, room_name)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 200)
        self.remove_room(site_id, room_id)
        rv = self.app.get('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 404)

        # Test that non authorized user can't delete room
        room_id = self.add_room(site_id, room_name)

        self.remove_admin('admin')
        rv = self.app.delete('/api/sites/{}/rooms/{}'.format(site_id, room_id))
        self.assertEqual(rv.status_code, 401)

    def test_room_put_without_data(self):
        rv = self.app.put('/api/sites/100/rooms/100')
        self.assertEqual(rv.status_code, 400)
