import flask


app = flask.Flask(__name__)

books = []


@app.route('/')
def hello():
    return flask.render_template('index.html', a_variable='testing')


@app.route('/books', methods=['GET'])
def list_books():
    return ' '.join(books)


@app.route('/books', methods=['POST'])
def get_books():
    books.append(flask.request.form['isbn'])
    return "ok"


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
