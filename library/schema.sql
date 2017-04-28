drop table if exists books;
create table books (
    id integer primary key autoincrement,
    isbn integer not null
);
