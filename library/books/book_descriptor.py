import library.database as database
from library.books.basic_book import BookError, BookNotFound, BasicBook


class BookDescriptor(BasicBook):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate()

    @staticmethod
    def get(isbn):
        db = database.get()
        curs = db.execute('SELECT * FROM book_descriptors '
                          'WHERE isbn = ?', (isbn,))

        book = curs.fetchall()
        if len(book) == 0:
            raise BookNotFound

        book = dict(book[0])
        book = BookDescriptor(**book)
        book.authors = book.get_authors()
        return book

    def exists(self):
        db = database.get()
        curs = db.execute('SELECT * FROM books WHERE isbn = ?',
                          (self.isbn,))

        books = curs.fetchall()
        if len(books) == 0:
            return False

        return True

    def add(self):
        db = database.get()
        db.execute('INSERT INTO book_descriptors'
                   '(isbn, title, pages, publisher, format,'
                   'publication_date, description, thumbnail)'
                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   self._get_params())
        self.add_authors(self.authors)
        db.commit()

    def update(self):
        db = database.get()
        db.execute('UPDATE book_descriptors '
                   'SET isbn = ?, title = ?, pages = ?, '
                   'publisher = ?, format = ?, publication_date = ?, '
                   'description = ?, thumbnail = ?',
                   self._get_params())
        self.update_authors(self.authors)
        db.commit()

    def add_authors(self, authors):
        db = database.get()
        db.execute('DELETE FROM authors WHERE isbn = ?',
                   (self.isbn,))
        for author in authors:
            db.execute(
                'INSERT INTO authors (isbn, name) VALUES (?, ?)',
                (self.isbn, author))

        db.commit()

    def update_authors(self, authors):
        self.add_authors(authors)

    def marshal(self):
        return vars(self)

    def get_authors(self):
        db = database.get()
        curs = db.execute('SELECT * FROM authors WHERE isbn = ?',
                          (self.isbn,))

        authors = []
        for author in curs.fetchall():
            authors.append(author['name'])

        return authors

    def need_update(self):
        db = database.get()
        curs = db.execute('SELECT * FROM book_descriptors WHERE isbn = ?',
                          (self.isbn,))

        descriptors = curs.fetchall()
        # Check if ISBN needs update
        descriptor = dict(descriptors[0])
        book_params = vars(self)
        equal = True
        for key in descriptor.keys():
            if descriptor[key] != book_params[key]:
                equal = False
                break

        return equal

    def validate(self):
        # Check some prerequesite
        if self.isbn is None:
            raise BookError('No ISBN present')

        try:
            int(self.isbn)
            int(self.pages)
        except ValueError:
            raise BookError('Non number in parameter where number is expected')
