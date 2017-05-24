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
    pages INTEGER,
    format TEXT,
    publisher TEXT,
    thumbnail BLOB
);

create table authors (
    author_id INTEGER primary key autoincrement,
    book_id INTEGER not null,
    name TEXT not null,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);

create table loans (
    loan_id INTEGER primary key autoincremenet,
    book_id INTEGER not null,
    employee_number INTEGER not null,
    loan_date INTEGER not null,
    return_date INTEGER,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
)
