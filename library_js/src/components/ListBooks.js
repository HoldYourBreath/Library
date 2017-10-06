import React from 'react';
import BookList from './BookList/';
import LocationSelector from './LocationSelector';
import locationStore from '../stores/LocationStore';
import { observer } from 'mobx-react';
const request = require('superagent');


class ListBooks extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        books: [],
        loadingBooks: false,
        siteIdFilter: 0,
        roomIdFilter: 0
      };
    }

    onSiteSelect(e) {
      let siteId = parseInt(e.target.value, 10);
      locationStore.selectSite(siteId);
      this.getBooksForSite(siteId);
    }

    getBooksForSite(site_id){
      this.setState({loadingBooks: true});
      request
      .get(`${window.API_URL}/api/books?site_id=${site_id}`)
      .type('application/json')
      .end((err, res) => {
        let currentBooks = res ? res.body : [];
        this.setState({
          loadingBooks: false,
          books: currentBooks});
      });
    }
    componentWillMount() {
      if (locationStore.selectedSite) {
        this.getBooksForSite(locationStore.selectedSite);
      }
    }

    render() {
      let currentBooks = this.state.books;
      if (locationStore.selectedRoom) {
        currentBooks = currentBooks.filter(b => b.room_id === locationStore.selectedRoom);
      }

      return (
        <div>
          <LocationSelector
            onSiteSelect={this.onSiteSelect.bind(this)}
          />
          {locationStore.selectedSite ? 
            <BookList 
                books={currentBooks}/>:
            <div>Select site</div>
          }
        </div>
      )
    }
}

export default observer(ListBooks);
