import React from 'react';
import {Media,
        Button} from 'react-bootstrap';

const Book = ({book}) => (
 <Media>
    <Media.Body>
        <Media.Heading>{book.title}</Media.Heading>
    </Media.Body>
 </Media>
);

export default Book;
