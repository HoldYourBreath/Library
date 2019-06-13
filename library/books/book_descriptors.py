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
        sub_query_books = 'SELECT isbn, COUNT(book_id) AS num_copies ' \
                          'FROM books GROUP BY isbn'
        sub_query_authors = 'SELECT isbn, GROUP_CONCAT(name) AS authors ' \
                            'FROM authors GROUP BY isbn'
        query = 'SELECT book_descriptors.*, books.num_copies, ' \
                'authors.authors FROM book_descriptors ' \
                'LEFT JOIN ({}) books USING (isbn) ' \
                'LEFT JOIN ({}) authors USING (isbn)' \
                .format(sub_query_books, sub_query_authors)
        curs = db.execute(query)
        books = BookDescriptors()
        for book in curs.fetchall():
            if not book['isbn']:
                # No books found
                return books

            authors = book['authors']
            book = dict(book)
            if authors:
                book['authors'] = [author for author in authors.split(',')]
            else:
                book['authors'] = []
            book = BookDescriptor(**book)
            books.books.append(book)

        return books
