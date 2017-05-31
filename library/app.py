import os
import flask

from library.config import config

app = flask.Flask(__name__)
app.config.from_object(__name__)  # load config from this file , flaskr.py
app.secret_key = config.get('flask', 'secret_key')

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'library.db'),
))
