import flask
import urllib
import json
import xml.dom.minidom as minidom

from app import app
from config import config

GOODREAD_ISBN_SEARCH_URL = "https://www.goodreads.com/search/index.xml?key={KEY}&q={ISBN}"
GOODREAD_BOOK_URL = "https://www.goodreads.com/book/show/{BOOK_ID}?key={KEY}"

@app.route('/api/books/goodreads/<isbn>')
def get_book(isbn):
    book_id = lookup_goodreads_id(isbn)
    book = fetch_goodreads_book(book_id)
    return get_json_response(book)


def lookup_goodreads_id(isbn):
    url = GOODREAD_ISBN_SEARCH_URL.replace("{KEY}", config.get('Goodreads', 'api_key'))
    url = url.replace("{ISBN}", str(isbn))
    response = urllib.urlopen(url)

    raw = response.read()

    dom = minidom.parseString(raw)
    for el in dom.getElementsByTagName('best_book')[0].childNodes:
        if el.nodeName == 'id':
            return el.firstChild.nodeValue

    raise LookupError("Can't find a book id for ISBN: {}".format(isbn))


def fetch_goodreads_book(book_id):
    url = GOODREAD_BOOK_URL.replace("{KEY}", config.get('Goodreads', 'api_key'))
    url = url.replace("{BOOK_ID}", str(book_id))
    response = urllib.urlopen(url)

    raw = response.read()
    return minidom.parseString(raw)


def get_json_response(book):
    json_response = {
        'author': get_authors(book),
        'title': get_title(book),
        'publication_date': get_publication_date(book),
        'num_pages': get_num_pages(book),
        'description': get_description(book)
    }

    response = app.response_class(
        response=json.dumps(json_response),
        status=200,
        mimetype='application/json'
    )

    return response


def get_authors(book):
    authors = []
    for node in book.getElementsByTagName('authors')[0].getElementsByTagName('name'):
        authors.append(node.childNodes[0].nodeValue)

    return authors


def get_title(book):
    return book.getElementsByTagName('title')[0].childNodes[0].nodeValue


def get_publication_date(book):
    date = [book.getElementsByTagName('publication_year')[0].childNodes[0].nodeValue,
            book.getElementsByTagName('publication_month')[0].childNodes[0].nodeValue.zfill(2),
            book.getElementsByTagName('publication_day')[0].childNodes[0].nodeValue.zfill(2)]
    return ' '.join(date)


def get_description(book):
    description = book.getElementsByTagName('description')[0]

    if description.hasChildNodes():
        return description.childNodes[0].nodeValue

    return ''


def get_num_pages(book):
    return int(book.getElementsByTagName('num_pages')[0].childNodes[0].nodeValue)
