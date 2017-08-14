import React from 'react';
import {FormGroup, 
        Button, 
        Col,
        Row,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
import {addSite, renameSite, addRoom} from '../lib/sites';

class Site extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      newRoomName: ''
    }
  }
  handleNewRoomNameUpdate(e) {
    this.setState({newRoomName: e.target.value});
  }

  handleAddNewRoom(e) {
	if (!this.state.newRoomName) {
      alert("No new room name specified!");
	} else {
	  addRoom(this.props.site.id, this.state.newRoomName)
        .then(() => {
          this.props.locationUpdate();
        });
	}
  }

  render() {
    return (
      <div className="panel panel-default">
	    <div className="panel-heading">{this.props.site.name}</div>
	    <ul className="list-group">
          {this.props.site.rooms.map((room) => {
            return <li className="list-group-item">{room.name}</li>
          })}
	    </ul>
        <div className="input-group">
          <input type="text"
	        className="form-control"
	        placeholder="New room name ..."
	    	onChange={this.handleNewRoomNameUpdate.bind(this)} />
          <span className="input-group-btn">
            <button
	          className="btn btn-default"
	          type="button"
	    	  onClick={this.handleAddNewRoom.bind(this)}>Add</button>
          </span>
        </div>
	  </div>
    )
  }
}
			

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
	  addSite(this.state.newSiteName)
        .then(() => {
          this.props.locationUpdate();
        });
	}
  }

  render() {
    return (
  	<div>
  	  {this.props.sites.map((site) => {
  		  return <Site site={site} locationUpdate={this.props.locationUpdate}/>
  	  })}
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
			onClick={this.handleAddNewSite.bind(this)}
		  >
			  Add
		  </button>
  		</span>
  	  </div>
  	</div>
    )
  }
}


class AdminPage extends React.Component {
  render() {
    return (
      <div>
        <h1>Admin</h1>
		<h2>Sites</h2>
		<p>Add sites, rename sites and add rooms to sites</p>
		<Sites sites={this.props.sites} locationUpdate={this.props.locationUpdate}/>
		<p />
      </div>
    );
  }
}

export default AdminPage;
