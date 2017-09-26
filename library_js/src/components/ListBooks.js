import React from 'react';
import BookList from './BookList/';
import LocationSelector from './LocationSelector';
const request = require('superagent');


class ListBooks extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        books: [],
        siteIdFilter: 0,
        roomIdFilter: 0
      };
    }

    onRoomFilterChange(e) {
      this.setState({
        roomIdFilter: parseInt(e.target.value, 10)
      });
    }
    onSiteFilterChange(e) {
      this.setState({
        siteIdFilter:  parseInt(e.target.value, 10)
      });
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
      let currentBooks = this.state.books;
      if (this.state.roomIdFilter) {
        currentBooks = currentBooks.filter(b => b.room_id === this.state.roomIdFilter);
      }
      return (
        <div>
          <LocationSelector
            onRoomChange={this.onRoomFilterChange.bind(this)}
            onSiteChange={this.onSiteFilterChange.bind(this)}/>
          <BookList 
            books={currentBooks}/>
        </div>
      )
    }
}

export default ListBooks;
