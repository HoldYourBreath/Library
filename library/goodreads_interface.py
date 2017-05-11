import flask
import urllib
import json
import xml.dom.minidom as minidom

from app import app
from config import config

GOODREAD_URL = "https://www.goodreads.com/search/index.xml?key={KEY}&q={ISBN}"

@app.route('/api/books/goodread/<isbn>')
def get_book(isbn):
    reply = fetch_goodread(isbn)
    dom = minidom.parseString(reply)
    book = dom.getElementsByTagName('best_book')[0]
    author = book.getElementsByTagName('author')[0].getElementsByTagName('name')[0].childNodes[0].nodeValue
    title = book.getElementsByTagName('title')[0].childNodes[0].nodeValue
    pub_date = [dom.getElementsByTagName('original_publication_year')[0].childNodes[0].nodeValue,
            dom.getElementsByTagName('original_publication_month')[0].childNodes[0].nodeValue,
            dom.getElementsByTagName('original_publication_day')[0].childNodes[0].nodeValue]

    response = {
            'author': author,
            'title': title,
            'publication_date': ' '.join(pub_date)
            }
    return json.dumps(response)


def fetch_goodread(isbn):
    url = GOODREAD_URL.replace("{KEY}", config.get('Goodreads', 'api_key')).replace("{ISBN}", str(isbn))
    response = urllib.urlopen(url)
    if response.getcode() != 200:
        raise InfobankHttpError(response.getcode(), url)

    raw = response.read()
    return raw
