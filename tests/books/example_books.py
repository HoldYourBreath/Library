import copy


book1 = {'isbn': 1234,
         'title': 'The book',
         'authors': ['Bob Author', 'Helio Author'],
         'pages': 500,
         'format': 'Slippery back',
         'publisher': 'Crazy dude publishing',
         'publication_date': '1820 01 02',
         'description': 'a book',
         'thumbnail': 'a thumbnail'}

book2 = {'isbn': 1235,
         'title': 'Great book',
         'authors': ['Jane Author'],
         'pages': 123,
         'room_id': 2,
         'format': 'Sturdy thing',
         'publisher': 'Sane gal publishing',
         'publication_date': '2016 12 31',
         'description': 'Another book',
         'thumbnail': 'another thumbnail'}

book3 = {'isbn': 1236,
         'title': 'Great Songs',
         'authors': ['Jane Author'],
         'pages': 100,
         'format': 'Sturdy thing',
         'publisher': 'Sane gal publishing',
         'publication_date': '2000 01 01',
         'description':
         'A very nice book about songs! All the best artists',
         'thumbnail': 'another thumbnail'}

book4 = {'isbn': 1237,
         'title': 'Great Poems',
         'authors': ['Jane Author'],
         'pages': 3,
         'format': 'Sturdy thing',
         'publisher': 'Sane gal publishing',
         'publication_date': '1999 12 31',
         'description':
         'A very nice book about poems! All the best poets',
         'thumbnail': 'another thumbnail'}


def get_book(book, book_id=1, room_id=1):
    temp_book = copy.copy(book)
    temp_book['book_id'] = book_id
    temp_book['room_id'] = room_id
    return temp_book
