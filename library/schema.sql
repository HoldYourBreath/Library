drop table if exists books;
create table books (
    id integer primary key autoincrement,
    tag interger not null unique,
    isbn integer not null
);
