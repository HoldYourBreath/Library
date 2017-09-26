import React  from 'react';
import locationStore from '../../stores/LocationStore';
import { observer } from 'mobx-react';
import Site from './Site';


class Sites extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      newSiteName: ''
    }
  }
  handleNewSiteNameUpdate(e) {
    this.setState({newSiteName: e.target.value});
  }
  
  handleAddNewSite(e) {
    if (!this.state.newSiteName) {
      alert("No new site name specified!");
    } else {
      locationStore.postNewSite(this.state.newSiteName);
    }
  }
  
  render() {
    return (
      <div>
        {locationStore.sites.map((site, i) =>
          <Site key={i} site={site} locationUpdate={this.props.locationUpdate}/>
        )}
        <h3>Add a new site</h3>
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            placeholder="New site name ..."
            onChange={this.handleNewSiteNameUpdate.bind(this)} />
          <span className="input-group-btn">
            <button
              className="btn btn-default"
              type="button"
              onClick={this.handleAddNewSite.bind(this)}>
              <span className="glyphicon glyphicon-ok" style={{color: "green"}} />
            </button>
          </span>
        </div>
      </div>
    )
  }
}

export default observer(Sites);
