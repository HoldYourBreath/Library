import library.database as database
from library.books.basic_book import BookError, BookNotFound
from library.books.book_descriptor import BookDescriptor
import library.loan as loan


class Book(BookDescriptor):
    def __init__(self, book_id, **kwargs):
        self.room_id = None
        super().__init__(**kwargs)
        self.book_id = book_id
        self.loaned = self.is_loaned()

    @staticmethod
    def exists(book_id):
        db = database.get()
        curs = db.execute('SELECT * FROM books WHERE book_id = ?',
                          (book_id,))

        books = curs.fetchall()
        if len(books) == 0:
            return False

        return True

    @staticmethod
    def get(book_id):
        db = database.get()
        author_query = "SELECT group_concat(name) " \
                       "FROM authors WHERE isbn = books.isbn"
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
        if authors:
            book['authors'] = [author for author in authors.split(',')]
        else:
            book['authors'] = []

        del book['book_id']
        book = Book(book_id, **book)
        book.authors = book.get_authors()
        return book

    def add(self):
        self.validate()

        # Check book descriptor
        if not super().exists():
            super().add()
        else:
            super().update()

        db = database.get()
        db.execute('INSERT INTO books'
                   '(book_id, isbn, room_id) '
                   'VALUES (?, ?, ?)',
                   (self.book_id, self.isbn, self.room_id))
        db.commit()

    def update(self):
        self.validate()

        # Check book descriptor
        if not super().exists():
            super().add()
        else:
            super().update()

        db = database.get()
        db.execute('UPDATE books '
                   'SET isbn = ?, room_id = ? '
                   'WHERE book_id = ?',
                   (self.isbn, self.room_id, self.book_id))
        db.commit()

    def validate(self):
        # @TODO: Check book ID format
        try:
            int(self.pages)
        except (ValueError, TypeError):
            raise BookError("pages missing or not an integer")
        try:
            int(self.isbn)
        except (ValueError, TypeError):
            raise BookError("isbn missing or not an integer")

        pass

    def marshal(self):
        json_book = vars(self)
        del json_book['number_of_copies']

        return json_book

    def is_loaned(self):
        try:
            search_only_active = True
            loan.by_book_id(self.book_id, search_only_active)
        except loan.LoanNotFound:
            return False

        return True


class Books():
    def __init__(self):
        self.books = []

    def marshal(self):
        return [book.marshal() for book in self.books]

    @staticmethod
    def get(search_params={}):
        db = database.get()
        author_query = "SELECT group_concat(name) " \
                       "FROM authors WHERE isbn = books.isbn"
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
