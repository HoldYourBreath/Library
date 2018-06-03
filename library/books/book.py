import library.database as database


class BookError(Exception):
    def __init__(self, message):
        self.msg = message


class BookNotFound(Exception):
    pass


class Book:
    def __init__(self, book_id, **kwargs):
        self.book_id = book_id
        self.isbn = None
        self.room_id = None
        self.title = ''
        self.authors = []
        self.description = ''
        self.thumbnail = ''
        self.pages = 0
        self.publisher = ''
        self.format = ''
        self.publication_date = ''
        self.loaned = False

        for parameter in vars(self):
            if parameter in kwargs:
                setattr(self, parameter, kwargs[parameter])

        self.loaned = 'loan_id' in kwargs and \
            kwargs['loan_id'] is not None and \
            kwargs['return_date'] is None

    @staticmethod
    def get(book_id):
        db = database.get()
        curs = db.execute('SELECT *, MAX(loans.loan_date) '
                          'FROM books '
                          'LEFT JOIN book_descriptors USING (isbn) '
                          'LEFT JOIN loans USING (book_id) '
                          'WHERE books.book_id = ? '
                          'GROUP BY book_id',
                          (book_id,))

        book = curs.fetchall()
        if len(book) == 0:
            raise BookNotFound

        book = dict(book[0])
        del book['book_id']
        book['loaned'] = book['loan_id'] is not None and \
            book['return_date'] is None
        book = Book(book_id, **book)
        book.authors = book.get_authors()
        return book

    def exists(self):
        db = database.get()
        curs = db.execute('SELECT * FROM books WHERE book_id = ?',
                          (self.book_id,))

        books = curs.fetchall()
        if len(books) == 0:
            return False

        return True

    def add(self):
        self.validate()
        self.check_isbn()
        db = database.get()
        db.execute('INSERT INTO books'
                   '(book_id, isbn, room_id) '
                   'VALUES (?, ?, ?)',
                   (self.book_id, self.isbn, self.room_id))
        db.commit()

    def update(self):
        self.validate()
        self.check_isbn()
        db = database.get()
        db.execute('UPDATE books '
                   'SET room_id = ?',
                   (self.room_id,))
        db.commit()

    def update_isbn(self):
        db = database.get()
        db.execute('UPDATE book_descriptors '
                   'SET isbn = ?, title = ?, pages = ?, '
                   'publisher = ?, format = ?, publication_date = ?, '
                   'description = ?, thumbnail = ? '
                   'WHERE book_id=?',
                   self._get_params())
        db.commit()

    def add_authors(self, authors):
        db = database.get()
        for author in authors:
            db.execute(
                'INSERT INTO authors (book_id, name) VALUES (?, ?)',
                (self.book_id, author))

        db.commit()

    def update_authors(self, authors):
        db = database.get()
        db.execute('DELETE FROM authors WHERE book_id = ?',
                   (self.book_id,))
        self.add_authors(authors)

    def marshal(self):
        json_book = vars(self)

        # Rename book_id to id
        book_id = json_book['book_id']
        del json_book['book_id']
        json_book['id'] = book_id

        return json_book

    def get_authors(self):
        db = database.get()
        curs = db.execute('SELECT * FROM authors WHERE book_id = ?',
                          (self.book_id,))

        authors = []
        for author in curs.fetchall():
            authors.append(author['name'])

        return authors

    def _get_params(self):
        return (self.isbn,
                self.title,
                self.pages,
                self.publisher,
                self.format,
                self.publication_date,
                self.description,
                self.thumbnail)

    def check_isbn(self):
        db = database.get()
        curs = db.execute('SELECT * FROM book_descriptors WHERE isbn = ?',
                          (self.isbn,))

        descriptors = curs.fetchall()
        if len(descriptors) == 0:
            # Add ISBN
            db.execute('INSERT INTO book_descriptors'
                       '(isbn, title, pages, publisher, format,'
                       'publication_date, description, thumbnail)'
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       self._get_params())
            db.commit()
        else:
            # Check if ISBN needs update
            descriptor = dict(descriptors[0])
            book_params = vars(self)
            equal = True
            for key in descriptor.keys():
                if descriptor[key] != book_params[key]:
                    equal = False
                    break
            if not equal:
                self.update_isbn()

    def validate(self):
        # Check some prerequesite
        if self.isbn is None:
            raise BookError('No ISBN present')
        elif self.room_id is None:
            raise BookError('No room_id present')

        # Check integer parameter constraints
        try:
            int(self.room_id)
        except ValueError:
            raise BookError('room_id is not a number')

        try:
            int(self.isbn)
            int(self.pages)
        except ValueError:
            raise BookError('Non number in parameter where number is expected')
