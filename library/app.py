import os
import flask

from library.config import config
from flask_cors import CORS


app = flask.Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config.from_object(__name__)  # load config from this file , flaskr.py
app.secret_key = config.get('flask', 'secret_key')

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'library.db'),
))


@app.before_first_request
def validate_database():
    from library.database import validate_db
    validate_db()
