from library.app import app
import library.loan as loan
import flask
from flask import jsonify



@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    """
    """
    return jsonify(loan.get_all())


@app.route('/api/loans', methods=['POST'])
def create_loan():
    put_data = flask.request.get_json()
    if put_data is None:
        response = jsonify({'msg': 'Missing json data in put request.'})
        response.status_code = 400
        return response
    elif 'user_id' not in put_data:
        response = jsonify({'msg': 'Missing user_id in put request.'})
        response.status_code = 400
        return response
    elif 'book_id' not in put_data:
        response = jsonify({'msg': 'Missing book_id in put request.'})
        response.status_code = 400
        return response

    loan_id = loan.add(put_data['book_id'], put_data['user_id'])
    return jsonify(loan.get(loan_id))


@app.route('/api/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    """
    """
    return jsonify(loan.get(loan_id))


@app.route('/api/loans/<int:loan_id>', methods=['DELETE'])
def remove_loan(loan_id):
    """
    """
    return jsonify(loan.remove(loan_id))
