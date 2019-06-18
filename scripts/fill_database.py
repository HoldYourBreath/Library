import http.client as client
import json
import codecs
import pprint
import os
import sys

# Add application top directory
script_path = os.path.join(os.path.dirname(__file__), '..')
app_path = os.path.abspath(script_path)
sys.path.append(app_path)

from tests.books.example_books import get_book, book1, book2, book3, book4

pp = pprint.PrettyPrinter()


header = {'Content-Type': "application/json"}

def get_connection():
    return client.HTTPConnection("localhost", 3001)


def check_site_and_room():
    conn = get_connection()
    conn.request("GET", "/api/sites/1")
    if conn.getresponse().status != 200:
        conn.request("POST", "/api/sites",
                     body=json.dumps({'name': 'Mountain hall'}),
                     headers=header)
        print_response(conn)

    conn.request("GET", "/api/sites/1/rooms/1")
    if conn.getresponse().status != 200:
        conn.request("POST", "/api/sites/1/rooms",
                     body=json.dumps({'name': 'Throne room'}),
                     headers=header)
        print_response(conn)


def print_response(conn):
    resp = conn.getresponse()
    print(resp.status)
    print(resp.msg)
    body = codecs.decode(resp.read())
    try:
        pp.pprint(json.loads(body))
    except json.decoder.JSONDecodeError:
        pass


def add_book(book, ebid):
    del book['book_id']
    conn = get_connection()
    conn.request("PUT", "/api/books/ebids/{}".format(ebid),
                 body=json.dumps(book),
                 headers=header)
    print_response(conn)


def print_all_books():
    conn = get_connection()
    conn.request("GET", "/api/books")
    print_response(conn)


if __name__ == "__main__":
    check_site_and_room()
    for i in range(1, 10):
        add_book(get_book(book1, book_id=i), i)
    for i in range(10, 15):
        add_book(get_book(book2, book_id=i), i)
    for i in range(15, 18):
        add_book(get_book(book3, book_id=i), i)
    for i in range(18, 30):
        add_book(get_book(book4, book_id=i), i)
    print_all_books()
