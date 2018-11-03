import library.database as database
from library.books.book_descriptor import BookDescriptor


class BookDescriptors:
    def __init__(self):
        self.books = []

    def marshal(self):
        return [book.marshal() for book in self.books]

    @staticmethod
    def get(search_params={}):
        db = database.get()
        author_query = "SELECT group_concat(name) " \
                       "FROM authors WHERE isbn = book_descriptors.isbn"
        query = 'SELECT book_descriptors.*, ' \
                '({}) AS authors, ' \
                'COUNT(books.book_id) AS num_books FROM book_descriptors ' \
                'LEFT JOIN books USING (isbn) ' .format(author_query)
        curs = db.execute(query)
        books = BookDescriptors()
        for book in curs.fetchall():
            if not book['isbn']:
                # No books found
                return books

            authors = book['authors']
            book = dict(book)
            if authors:
                book['authors'] = [book for book in authors.split(',')]
            else:
                book['authors'] = []
            book = BookDescriptor(**book)
            books.books.append(book)

        return books
