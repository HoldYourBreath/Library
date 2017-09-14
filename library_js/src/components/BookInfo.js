import React from 'react';

const BookInfo = ({bookData}) => (
  <div>
    <div style={{fontWeight: 'bold'}}>Book Info:</div>
    <div>Title: {bookData.title}</div>
    <div>Id: {bookData.id}</div>
    <div>ISBN: {bookData.email}</div>
  </div>
);

export default BookInfo;