drop table if exists books;
drop table if exists authors;
drop table if exists author_works;

create table books (
    book_id INTEGER primary key autoincrement,
    tag INTEGER not null unique,
    isbn INTEGER not null,
    title TEXT,
    description TEXT,
    publication_date TEXT,
    thumbnail BLOB
);

create table authors (
    author_id INTEGER primary key autoincrement,
    book_id INTEGER,
    name TEXT,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);
