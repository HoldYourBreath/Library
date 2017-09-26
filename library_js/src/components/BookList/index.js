import React from 'react';
import { Table } from 'react-bootstrap';
import TableRow from './TableRow';


class BookList extends React.Component {
  constructor() {
    super();
    this.state = {};
  };
  render() {
    console.log(this.props);
    return (
      <div>
        <Table striped bordered condensed hover>
          <thead>
            <tr>
              <th></th>
              <th>Author</th>
              <th>Title</th>
              <th>ISBN</th>
            </tr>
          </thead>
          <tbody>
            {this.props.books.map((book, i) => {
              return <TableRow 
                        key={i}
                        bookData={book}/>
            })}
          </tbody>
        </Table>
      </div>
    )
  }
}

export default BookList;
