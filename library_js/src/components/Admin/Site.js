import React from 'react';
import locationStore from '../../stores/LocationStore';
import Room from './Room';
import { observer } from 'mobx-react';
import { addRoom } from '../../lib/sites';


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
    addRoom(this.props.site.siteId, this.state.newRoomName)
      .then(() => {
        this.props.locationUpdate();
      });
    }
  }
  
  render() {
    let rooms = locationStore.rooms.filter(r => this.props.site.siteId === r.siteId);
    return (
      <div className="panel panel-default">
      <div className="panel-heading">{this.props.site.siteName}</div>
      <ul className="list-group">
        {rooms.map((room, i) => {
          return <Room 
                    site_id={this.props.site.siteId}
                    key={i}
                    room={room}/>
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

export default Site;
