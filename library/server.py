import os
import sqlite3
import flask


app = flask.Flask(__name__)
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'library.db'),
))

books = []


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    """Connects to the specific database."""
    db_path = app.config['DATABASE']
    rv = sqlite3.connect(db_path)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = connect_db()
    return flask.g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.close()


@app.route('/')
def hello():
    return flask.render_template('index.html', a_variable='testing')


@app.route('/books', methods=['GET'])
def list_books():
    db = get_db()
    curs = db.execute('select isbn from books order by id desc')
    books = [str(row[0]) for row in curs.fetchall()]

    return ' '.join(books)


@app.route('/books/<book_id>', methods=['PUT'])
def get_books(book_id):
    isbn = flask.request.form['isbn']
    db = get_db()
    db.execute('delete from books where tag=?', (int(book_id),))
    db.execute('insert into books (tag, isbn) values (?, ?)', (int(book_id), int(isbn)))
    db.commit()
    return "ok"


@app.route('/books/<isbn>', methods=['POST'])
def get_single_book():
    return 'NOT IMPLEMENTED'


def _get_book(book_id):
    db = get_db()
    curs = db.execute('select * from books where tag = ?', (book_id,))
    if curs.rowcount == 0:
        raise BookNotFound

    book = curs.fetchone()

    json_book = {
            'tag': book.tag,
            'isbn': book.isbn,
            }

    return json_book


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
