drop table if exists books;
drop table if exists authors;
drop table if exists loans;
drop table if exists sites;
drop table if exists rooms;
drop table if exists admins;
drop table if exists sessions;

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
    room_id INTEGER not null,
    thumbnail BLOB,
    FOREIGN KEY(room_id) REFERENCES rooms(room_id)
);

create table authors (
    author_id INTEGER primary key autoincrement,
    book_id INTEGER not null,
    name TEXT not null,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);

create table sites (
    site_id INTEGER primary key autoincrement,
    site_name TEXT not null unique
);

create table rooms (
    room_id INTEGER primary key autoincrement,
    site_id INTEGER not null,
    room_name TEXT not null unique,
    FOREIGN KEY(site_id) REFERENCES sites(site_id)
);

create table loans (
    loan_id INTEGER primary key autoincrement,
    book_id INTEGER not null,
    employee_number INTEGER not null,
    loan_date INTEGER not null,
    return_date INTEGER,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);

create table sessions (
    session_id TEXT primary key,
    user_id TEXT not null,
    login_time TIMESTAMP not null,
    last_activity TIMESTAMP not null
);

create table admins (
    admin_id INTEGER primary key autoincrement,
    signum TEXT not null unique,
    admin_level INTEGER not null
);
