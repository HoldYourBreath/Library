import library.database as database
from library.books.book import Book


class Books:
    def __init__(self):

        self.books = []

    def marshal(self):
        return [book.marshal() for book in self.books]

    @staticmethod
    def get(search_params={}):
        db = database.get()
        (query, query_params) = Books._get_query(search_params)

        curs = db.execute(query, tuple(query_params))
        books = Books()
        for book in curs.fetchall():
            book = dict(book)
            book_id = book['book_id']
            del book['book_id']
            book = Book(book_id, **book)
            book.authors = book.get_authors()
            books.books.append(book)

        return books

    @staticmethod
    def _get_query(search_params):
        wheres = []
        query_params = []

        if 'isbn' in search_params:
            wheres.append(' WHERE books.isbn = ?')
            query_params.append(search_params['isbn'])

        if 'title' in search_params:
            wheres.append(' WHERE books.title LIKE ?')
            query_params.append('%' + search_params['title'] + '%')

        if 'description' in search_params:
            wheres.append(' WHERE books.description LIKE ?')
            query_params.append('%' + search_params['description'] + '%')

        if 'room_id' in search_params:
            wheres.append(' WHERE books.room_id = ?')
            query_params.append(search_params['room_id'])

        if 'site' in search_params:
            wheres.append(' WHERE sites.site_name LIKE ?')
            query_params.append('%' + search_params['site'] + '%')

        if 'site_id' in search_params:
            wheres.append(' WHERE sites.site_id = ?')
            query_params.append(search_params['site_id'])

        if 'loaned' in search_params:
            loaned = search_params['loaned'].lower()
            if 'true' in loaned:
                wheres.append(' WHERE loans.loan_id IS NOT NULL')
            elif 'false' in loaned:
                wheres.append(' WHERE loans.loan_id IS NULL')

        if 'room' in search_params:
            wheres.append(' WHERE rooms.room_name LIKE ?')
            query_params.append('%' + search_params['room'] + '%')

        where_conditions = ''
        if len(wheres) > 0:
            for where in wheres:
                where_conditions += where.replace('WHERE', 'AND')

        query = 'SELECT *, COUNT(book_id) AS num_books ' \
                'FROM books ' \
                'LEFT JOIN loans USING (book_id) ' \
                'LEFT JOIN rooms USING (room_id) ' \
                'LEFT JOIN sites USING (site_id) ' \
                'WHERE loans.return_date IS NULL ' \
                '{} GROUP BY isbn ORDER BY book_id '

        query = query.format(where_conditions)
        return (query, query_params)
