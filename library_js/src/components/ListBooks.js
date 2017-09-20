import React from 'react';
import Books from './books';
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
        .get(`${window.__appUrl}/api/books`)
        .type('application/json')
        .end((err, res) => {
          let currentBooks = res ? res.body : [];
          this.setState({books: currentBooks});
        });
    }

    render() {
      console.log(this.props);
      return (
        <Books books={this.state.books}/>
      )
    }
}

export default ListBooks;
