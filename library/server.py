import flask
from flask import send_from_directory

from library.app import app
import library.api as api
import library.goodreads_interface
import library.user_lookup
import library.api_loan
import library.api_location
import library.session as session


@app.route('/static/<path:path>')
def serve_static(path):
    print("path: {}".format(path))
    return send_from_directory('static', path)


def run(args):
    if args.fake_auth:
        print('Faking authentication')
        session.AUTHENTICATE = False
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0')


if __name__ == "__main__":
    run()
