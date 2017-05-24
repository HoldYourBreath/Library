import urllib
from flask import json, jsonify

from library.config import config
from library.app import app


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    request_url = config.get('udb', 'url') + "/user/employeeNumber/{}".format(user_id)
    try:
        response = urllib.request.urlopen(request_url)
    except urllib.error.HTTPError as err:
        response = jsonify({'message': 'Failed to fetch user information for: {}'.format(user_id)})
        response.status_code = err.code
        return response
    data = response.read().decode("utf-8")
    json_data = json.loads(data)
    return jsonify(json_data)

