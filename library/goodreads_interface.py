import urllib
import json
import xml.dom.minidom as minidom

from library.app import app
from library.config import config

GOODREADS_URL = "https://www.goodreads.com"
GOODREADS_ISBN_SEARCH_URL = GOODREADS_URL + "/search/index.xml" \
                                            "?key={KEY}&q={ISBN}"
GOODREADS_BOOK_URL = GOODREADS_URL + "/book/show/{BOOK_ID}?key={KEY}"


@app.route('/api/books/goodreads/<isbn>')
def get_book(isbn):
    book_id = lookup_goodreads_id(isbn)
    book = fetch_goodreads_book(book_id)
    return get_json_response(book)


def lookup_goodreads_id(isbn):
    url = GOODREADS_ISBN_SEARCH_URL.replace(
        "{KEY}", config.get('Goodreads', 'api_key'))
    url = url.replace("{ISBN}", str(isbn))
    response = urllib.request.urlopen(url)

    raw = response.read()

    dom = minidom.parseString(raw)
    for el in dom.getElementsByTagName('best_book')[0].childNodes:
        if el.nodeName == 'id':
            return el.firstChild.nodeValue

    raise LookupError("Can't find a book id for ISBN: {}".format(isbn))


def fetch_goodreads_book(book_id):
    url = GOODREADS_BOOK_URL.replace(
        "{KEY}", config.get('Goodreads', 'api_key'))
    url = url.replace("{BOOK_ID}", str(book_id))
    response = urllib.request.urlopen(url)

    raw = response.read()
    return minidom.parseString(raw)


def get_json_response(book):
    json_response = {
        'author': get_authors(book),
        'title': get_title(book),
        'publication_date': get_publication_date(book),
        'num_pages': get_num_pages(book),
        'format': get_format(book),
        'publisher': get_publisher(book),
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
    nodes = book.getElementsByTagName('authors')[0] \
        .getElementsByTagName('name')
    for node in nodes:
        authors.append(node.childNodes[0].nodeValue)

    return authors


def get_title(book):
    if book.getElementsByTagName('title')[0].hasChildNodes():
        return book.getElementsByTagName('title')[0].childNodes[0].nodeValue

    # In the case of no title, return empty string
    return ''


def get_publication_date(book):
    if(not book.getElementsByTagName('publication_year')[0].hasChildNodes() or
       not book.getElementsByTagName('publication_month')[0].hasChildNodes() or
       not book.getElementsByTagName('publication_day')[0].hasChildNodes()):
        # In the case of no publication date, return empty date
        return ''

    year = book.getElementsByTagName('publication_year')[0] \
        .childNodes[0].nodeValue
    month = book.getElementsByTagName('publication_month')[0] \
        .childNodes[0].nodeValue
    day = book.getElementsByTagName('publication_day')[0] \
        .childNodes[0].nodeValue
    date = [year, month.zfill(2), day.zfill(2)]
    return ' '.join(date)


def get_description(book):
    description = book.getElementsByTagName('description')[0]

    if description.hasChildNodes():
        return description.childNodes[0].nodeValue

    # In the case of no description, return empty string
    return ''


def get_num_pages(book):
    if book.getElementsByTagName('num_pages')[0].hasChildNodes():
        return int(
            book.getElementsByTagName('num_pages')[0].childNodes[0].nodeValue)

    # In the case of no page num, return 0 pages
    return 0


def get_publisher(book):
    if book.getElementsByTagName('publisher')[0].hasChildNodes():
        return book.getElementsByTagName('publisher')[0] \
            .childNodes[0].nodeValue

    # In the case of no publisher, return empty string
    return ''


def get_format(book):
    if book.getElementsByTagName('format')[0].hasChildNodes():
        return book.getElementsByTagName('format')[0].childNodes[0].nodeValue

    # In the case of no format, return empty string
    return ''
