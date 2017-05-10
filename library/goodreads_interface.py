import flask
import urllib
import json

from app import app

GOODREAD_URL = "https://www.goodreads.com/search/index.xml?key={KEY}&q={ISBN}"
API_KEY = "PRIVATE"

@app.route('/api/books/goodread/<isbn>')
def get_book(isbn):
    reply = fetch_goodread(isbn)
    return reply


def fetch_goodread(isbn):
    url = GOODREAD_URL.replace("{KEY}", API_KEY).replace("{ISBN}", str(isbn))
    response = urllib.urlopen(url)
    if response.getcode() != 200:
        raise InfobankHttpError(response.getcode(), url)

    raw = response.read()
    return raw
