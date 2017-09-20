import sqlite3
from library.app import app
import library.database as database
import flask
from flask import jsonify
import library.session as session


class SiteNotFound(Exception):
    pass


class RoomNotFound(Exception):
    pass


def _serialize_sites(rooms):
    site_indexes = {}
    sites = []
    for room in rooms:
        site_id = room["site_id"]
        if site_id not in site_indexes.keys():
            # Store the index of this site id
            site_indexes[site_id] = len(sites)

            sites.append({
                "id": site_id,
                "name": room["site_name"],
                "rooms": []})

        if room["room_id"]:
            # It could be so that the left join returns an empty site
            site_index = site_indexes[site_id]
            sites[site_index]["rooms"].append({
                "id": room["room_id"],
                "name": room["room_name"]})

    return sites


def _serialize_room(room):
    return {"name": room["room_name"],
            "id": room["room_id"]}


def _serialize_rooms(rooms):
    return [_serialize_room(r) for r in rooms]


def _get_site(site_id):
    db_instance = database.get()
    curs = db_instance.execute('SELECT * FROM sites '
                               'LEFT JOIN rooms USING (site_id) '
                               'WHERE site_id = ? ', (site_id,))
    sites = curs.fetchall()
    if (len(sites) == 0):
        raise SiteNotFound

    return _serialize_sites(sites)[0]


def _get_sites():
    db_instance = database.get()
    curs = db_instance.execute('SELECT * FROM sites '
                               'LEFT JOIN rooms USING (site_id) '
                               'ORDER BY site_name DESC')
    rooms_cursor = curs.fetchall()
    return _serialize_sites(rooms_cursor)


def _get_room(room_id):
    db_instance = database.get()
    curs = db_instance.execute('SELECT * FROM rooms '
                               'WHERE room_id = ?',
                               (room_id,))
    rooms = curs.fetchall()
    if (len(rooms) == 0):
        raise RoomNotFound

    return _serialize_rooms(rooms)[0]


def _get_rooms(site_id):
    db_instance = database.get()
    curs = db_instance.execute(
        'SELECT * FROM rooms WHERE site_id = ? '
        'ORDER BY room_name DESC',
        (site_id,)
    )
    rooms = curs.fetchall()
    return _serialize_rooms(rooms)


@app.route('/api/sites', methods=['GET'])
def get_all_sites():
    """
    """
    return jsonify(_get_sites())


@app.route('/api/sites/<int:site_id>/rooms/<int:room_id>', methods=['DELETE'])
@session.admin_required
def delete_room(site_id, room_id):
    try:
        response = jsonify(_get_room(room_id))
    except RoomNotFound:
        response = jsonify({'msg': 'Room not found'})
        response.status_code = 404
        return response
    db = database.get()
    books_cursor = db.cursor()
    books_cursor.execute('SELECT * FROM books WHERE room_id = ?', (room_id,))
    books = books_cursor.fetchall()
    if len(books) == 0:
        books_cursor.execute(
            'DELETE FROM rooms '
            'WHERE room_id = ?', (room_id,))
        db.commit()
    else:
        response = jsonify({
            'msg': 'Room currently has books linked to it.\
          Make sure the room is empty before deleting this room'
        })
        response.status_code = 403
    return response


@app.route('/api/sites', methods=['POST'])
@session.admin_required
def add_new_site():
    """
    """
    post_data = flask.request.get_json()
    if post_data is None:
        response = jsonify({'msg': 'Missing json data in post request.'})
        response.status_code = 400
        return response
    elif 'name' not in post_data:
        response = jsonify({'msg': 'Missing site name in post request.'})
        response.status_code = 400
        return response

    try:
        db_instance = database.get()
        cursor = db_instance.cursor()
        cursor.execute(
            'INSERT INTO sites '
            '(site_name) VALUES (?)',
            (post_data['name'],)
        )
        db_instance.commit()
        last_id = cursor.lastrowid
        last_added_site = _get_site(last_id)
        response = jsonify(last_added_site)
        response.status_code = 200
    except sqlite3.IntegrityError as err:
        response = jsonify({"msg": "A site with that name already exist"})
        response.status_code = 409
    return response


@app.route('/api/sites/<int:site_id>', methods=['GET'])
def get_site(site_id):
    """
    """
    try:
        response = jsonify(_get_site(site_id))
    except SiteNotFound:
        response = jsonify({'msg': 'Site not found'})
        response.status_code = 404
        return response

    return response


@app.route('/api/sites/<int:site_id>', methods=['PUT'])
@session.admin_required
def rename_site(site_id):
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing data in put request.'})
        response.status_code = 400
        return response
    if 'name' in put_data:
        db = database.get()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE sites '
            'SET site_name = ? '
            'WHERE site_id = ?',
            (put_data['name'],
             site_id))
        db.commit()
    response = jsonify(_get_site(site_id))
    response.status_code = 200
    return response


@app.route('/api/sites/<int:site_id>/rooms', methods=['GET'])
def get_rooms(site_id):
    response = jsonify(_get_rooms(site_id))
    return jsonify(_get_rooms(site_id))


@app.route('/api/sites/<int:site_id>/rooms', methods=['POST'])
@session.admin_required
def post_new_room(site_id):
    """
    """
    post_data = flask.request.get_json()
    if post_data is None:
        response = jsonify({'msg': 'Missing json data in post request.'})
        response.status_code = 400
        return response
    elif 'name' not in post_data:
        response = jsonify(
            {'msg': 'Expected parameters in post request: name'})
        response.status_code = 400
        return response

    db_instance = database.get()
    existing_room = db_instance.execute(
        'SELECT * FROM rooms '
        'WHERE site_id = ? '
        'AND room_name = ?',
        (site_id, post_data['name'])
    )
    if len(existing_room.fetchall()) > 0:
        # Do not allow duplicate room names within a site
        response = jsonify({"msg": 'A name with that name already '
                            'exists for this site'})
        response.status_code = 409
        return response

    cursor = db_instance.cursor()
    cursor.execute(
        'INSERT INTO rooms '
        '(room_name, site_id) VALUES (?, ?)',
        (post_data['name'], site_id, )
    )
    db_instance.commit()
    last_id = cursor.lastrowid
    last_added_room = _get_room(last_id)
    response = jsonify(last_added_room)
    response.status_code = 200

    return response


@app.route('/api/sites/<int:site_id>/rooms/<int:room_id>', methods=['GET'])
def get_room(site_id, room_id):
    try:
        response = jsonify(_get_room(room_id))
    except RoomNotFound:
        response = jsonify({'msg': 'Room not found'})
        response.status_code = 404
        return response

    return response


@app.route('/api/sites/<int:site_id>/rooms/<int:room_id>', methods=['PUT'])
@session.admin_required
def rename_room(site_id, room_id):
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing data in put request.'})
        response.status_code = 400
        return response
    if 'name' in put_data:
        db = database.get()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE rooms '
            'SET room_name = ? '
            'WHERE room_id = ?',
            (put_data['name'],
             room_id))
        db.commit()
    response = jsonify(_get_room(room_id))
    response.status_code = 200
    return response
