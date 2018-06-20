import os
import logging
import flask

from library.config import config
from flask_cors import CORS


app = flask.Flask(__name__)

# Add logger
script_path = os.path.join(os.path.dirname(__file__), '..')
app_path = os.path.abspath(script_path)
log_path = os.path.join(app_path, 'log')
if not os.path.exists(log_path):
    os.makedirs(log_path)

fh = logging.FileHandler(os.path.join(log_path, 'library.log'))
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

app.logger.addHandler(fh)
app.logger.setLevel(logging.DEBUG)

# Remove default logger
app.logger.removeHandler(flask.logging.default_handler)

app.logger.info('Flask app up and running')

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
