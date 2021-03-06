drop table if exists sessions;
drop table if exists authors;
drop table if exists loans;
drop table if exists rooms;
drop table if exists sites;
drop table if exists admins;
drop table if exists book_instances;
drop table if exists books;

create table book_descriptors (
    isbn INTEGER primary key,
    title TEXT,
    description TEXT,
    publication_date TEXT,
    pages INTEGER,
    format TEXT,
    publisher TEXT,
    thumbnail BLOB
);

create table books (
    book_id INTEGER primary key,
    isbn INTEGER not null,
    room_id INTEGER not null,
    FOREIGN KEY(isbn) REFERENCES book_descriptors(isbn),
    FOREIGN KEY(room_id) REFERENCES rooms(room_id)
);

create table authors (
    author_id INTEGER primary key autoincrement,
    isbn INTEGER not null,
    name TEXT not null,
    FOREIGN KEY(isbn) REFERENCES book_descriptors(isbn)
);

create table sites (
    site_id INTEGER primary key autoincrement,
    site_name TEXT not null unique
);

create table rooms (
    room_id INTEGER primary key autoincrement,
    site_id INTEGER not null,
    room_name TEXT not null,
    FOREIGN KEY(site_id) REFERENCES sites(site_id)
);

create table loans (
    loan_id INTEGER primary key autoincrement,
    book_id INTEGER not null,
    user_id INTEGER not null,
    loan_date REAL not null,
    return_date REAL,
    due_date REAL,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);

create table sessions (
    session_id INTEGER primary key autoincrement,
    secret TEXT not null,
    user_id TEXT not null,
    login_time TIMESTAMP not null,
    last_activity TIMESTAMP not null
);

create table admins (
    admin_id INTEGER primary key autoincrement,
    user_id TEXT not null unique,
    admin_level INTEGER not null
);
