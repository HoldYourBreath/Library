import React from 'react';
import {InputGroup,
	    Glyphicon,
        Button,
        Alert,
        FormControl
        } from 'react-bootstrap';
import {addSite, addRoom, removeRoom, renameRoom} from '../lib/sites';
class Room extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      newRoomName: props.room.name,
	  edit: false,
	  errorMsg: null
    }
  }

  toggleEdit(e) {
	  this.setState({'edit': !this.state.edit});
  }

  handleRemoveRoom(e) {
    if (window.confirm("Are you sure you want to delete this room?") === true) {
    removeRoom(this.props.site_id, this.props.room.id)
        .then(() => {
            this.props.locationUpdate();
        })
        .catch((res) => {
            this.setState({errorMsg: res.msg});
        })
    };
  }

  handleNewNameChange(e) {
    this.setState({newRoomName: e.target.value});
  }

  handleRenameRoom(e) {
    if (this.state.newRoomName !== this.props.room.name) {
      renameRoom(this.props.site_id, this.props.room.id, this.state.newRoomName)
          .then(() => {
            this.props.locationUpdate();
          });
    }
  }

  render () {
    const ErrAlert = this.state.errorMsg ? <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null;
    if (this.state.edit) {
        return (
        <InputGroup>
          {ErrAlert}
          <FormControl
          type="text"
          defaultValue={this.state.newRoomName}
        onChange={this.handleNewNameChange.bind(this)} />
          <InputGroup.Button>
            <Button onClick={this.handleRemoveRoom.bind(this)}>
          <Glyphicon glyph="remove" style={{color: "red"}} />
          </Button>
          <Button onClick={this.handleRenameRoom.bind(this)}>
          <Glyphicon glyph="ok" style={{color: "green"}} />
        </Button>
        </InputGroup.Button>
      </InputGroup>
      )
    } else {
      return (
          <li className="list-group-item">{this.props.room.name}
            <a
          role="button"
          className="input-group-button"
          onClick= {this.toggleEdit.bind(this)}>
              <span
            className="glyphicon glyphicon-pencil pull-right"
          style={{color: 'gold'}}></span>
            </a>
          </li>
      )
    }
  }
}

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
			return <Room 
			  		 site_id={this.props.site.id}
			         room={room}
			         locationUpdate={this.props.locationUpdate} />
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
		  	  onClick={this.handleAddNewRoom.bind(this)}>
		       <span className="glyphicon glyphicon-ok" style={{color: "green"}} />
		    </button>
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
			onClick={this.handleAddNewSite.bind(this)}>
		    <span className="glyphicon glyphicon-ok" style={{color: "green"}} />
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
        <h1>Sites and rooms</h1>
		<p>Add sites, rename sites and add rooms to sites</p>
		<Sites sites={this.props.sites} locationUpdate={this.props.locationUpdate}/>
		<p />
      </div>
    );
  }
}

export default AdminPage;
