import sqlite3
from library.app import app
import library.database as database
import flask
from flask import jsonify

BOOK_LOAN_IN_DAYS = 14


def _serialize_site(s):
    return {
        "site_name": s["site_name"],
        "id": s["site_id"]}


def _get_sites():
    db_instance = database.get()
    curs = db_instance.execute('select * from sites order by site_name desc')
    sites_cursor = curs.fetchall()
    return [_serialize_site(s) for s in sites_cursor]


@app.route('/api/sites', methods=['GET'])
def get_all_sites():
    """
    """
    return jsonify(_get_sites())


@app.route('/api/loc/all', methods=['GET'])
def get_current_locations():
    """
    Get all rooms and all locations.

    :return:
    """
    return jsonify({'rooms': get_rooms(),
                    'sites': _get_sites()})


def get_rooms():
    db_instance = database.get()
    curs = db_instance.execute(
        'SELECT rooms.*, sites.* FROM rooms '
        'JOIN sites USING (site_id) '
        'ORDER BY room_name DESC')
    rooms_cursor = curs.fetchall()
    return [_serialize_room(r) for r in rooms_cursor]


@app.route('/api/sites/<int:site_id>', methods=['PUT'])
def rename_site(site_id):
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing data in put request.'})
        response.status_code = 500
        return response
    db = database.get()
    cursor = db.cursor()
    cursor.execute(
        'UPDATE sites '
        'SET site_name = ? '
        'WHERE site_id = ?',
        (put_data['name'],
         site_id))
    db.commit()
    response = jsonify({"msg": "OK"})
    response.status_code = 200
    return response


@app.route('/api/sites', methods=['POST'])
def add_new_site():
    """
    """
    post_data = flask.request.get_json()
    if post_data is None:
        response = jsonify({'msg': 'Missing json data in post request.'})
        response.status_code = 500
        return response
    elif 'name' not in post_data:
        response = jsonify({'msg': 'Missing site name in post request.'})
        response.status_code = 500
        return response

    try:
        db_instance = database.get()
        db_instance.execute(
            'INSERT INTO sites '
            '(site_name) VALUES (?)',
            (post_data['name'],)
        )
        db_instance.commit()
        response = jsonify({"msg": "OK"})
        response.status_code = 200
    except sqlite3.IntegrityError as err:
        response = jsonify({"msg": str(err)})
        response.status_code = 500
    return response


def _serialize_room(room):
    return {"room_name": room["site_name"] + "-" + room["room_name"],
            "site_id": room["site_id"],
            "id": room["room_id"]}


@app.route('/api/rooms', methods=['GET'])
def get_all_rooms():
    """
    """
    return jsonify(get_rooms())


@app.route('/api/rooms', methods=['POST'])
def post_new_room():
    """
    """
    post_data = flask.request.get_json()
    if post_data is None:
        response = jsonify({'msg': 'Missing json data in post request.'})
        response.status_code = 500
        return response
    elif 'name' not in post_data or 'site_id' not in post_data:
        response = jsonify(
            {'msg': 'Expected parameters in post request: name, site_id'})
        response.status_code = 500
        return response

    try:
        db_instance = database.get()
        db_instance.execute(
            'INSERT INTO rooms '
            '(room_name, site_id) VALUES (?, ?)',
            (post_data['name'], 1, )
        )
        db_instance.commit()
        response = jsonify({"msg": "OK"})
        response.status_code = 200
    except sqlite3.IntegrityError as err:
        response = jsonify({"msg": str(err)})
        response.status_code = 500
    return response
