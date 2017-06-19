import React, { Component } from 'react';
import Book from './book.js';
const request = require('superagent');


class Books extends Component {
  constructor(props) {
    super(props);
    this.state = {
      books: []
    };
  }
  componentWillMount() {
    console.log("Get books");
    ;
    request
      .get(`${window.__appUrl}/api/books`)
      .type('application/json')
      .end((err, res) => {
        this.setState({books: res.body});
      });
  }
  render() {
    return (
      <div>
        <h1>
            Books
        </h1>
        <ul>
        {
          this.state.books.map((book, i) => {
            return <Book
                    key={i}
                    book={book}/>
                })
          }
          </ul>
      </div>

    );
  }
}

export default Books;
