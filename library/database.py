import flask
import sqlite3

from app import app


def init():
    db = get()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()


def connect():
    """Connects to the specific database."""
    db_path = app.config['DATABASE']
    rv = sqlite3.connect(db_path)
    rv.row_factory = sqlite3.Row
    return rv


def get():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = connect()

    return flask.g.sqlite_db


@app.teardown_appcontext
def close(error):
    """Closes the database again at the end of the request."""
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.close()
