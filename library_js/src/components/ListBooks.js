import React from 'react';
import BookList from './BookList/';
const request = require('superagent');


class ListBooks extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        books: []
      };
    }

    componentWillMount() {
      request
        .get(`${window.API_URL}/api/books`)
        .type('application/json')
        .end((err, res) => {
          let currentBooks = res ? res.body : [];
          this.setState({books: currentBooks});
        });
    }

    render() {
      console.log(this.props);
      return (
        <BookList books={this.state.books}/>
      )
    }
}

export default ListBooks;
