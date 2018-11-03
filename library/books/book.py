import library.database as database
from library.books.basic_book import BookError, BookNotFound
from library.books.book_descriptor import BookDescriptor


class Book(BookDescriptor):
    def __init__(self, book_id, **kwargs):
        self.room_id = None
        super().__init__(**kwargs)
        self.book_id = book_id

    @staticmethod
    def get(book_id):
        db = database.get()
        author_query = "SELECT group_concat(name) FROM authors WHERE isbn = books.isbn"
        curs = db.execute("SELECT *, ({}) as authors "
                          "FROM books "
                          "LEFT JOIN book_descriptors "
                          "USING (isbn) "
                          "WHERE book_id = ?".format(author_query), (book_id,))

        book = curs.fetchall()
        if len(book) == 0:
            raise BookNotFound

        authors = book[0]['authors']
        book = dict(book[0])
        book['authors'] = [author for author in authors.split(',')]

        del book['book_id']
        book = Book(book_id, **book)
        book.authors = book.get_authors()
        return book

    def add(self):
        self.validate()
        db = database.get()

        # Check book descriptor
        if not super().exists():
            super().add()
        else:
            super().update()

        db.execute('INSERT INTO books'
                   '(book_id, isbn, room_id) '
                   'VALUES (?, ?, ?)',
                   (self.book_id, self.isbn, self.room_id))
        db.commit()

    def exists(self):
        return False

    def validate(self):
        # @TODO: Check book ID format
        pass

    def marshal(self):
        json_book = vars(self)

        return json_book


class Books():
    def __init__(self):
        self.books = []

    def marshal(self):
        return [book.marshal() for book in self.books]

    @staticmethod
    def get(search_params={}):
        db = database.get()
        author_query = "SELECT group_concat(name) FROM authors WHERE isbn = books.isbn"
        curs = db.execute("SELECT *, ({}) as authors "
                          "FROM books LEFT JOIN book_descriptors "
                          "USING (isbn)".format(author_query))
        books = Books()
        for book in curs.fetchall():
            authors = book['authors']
            book = dict(book)
            book['authors'] = [author for author in authors.split(',')]
            book_id = book['book_id']
            del book['book_id']
            new_book = Book(book_id, **book)
            books.books.append(new_book)

        return books
