import React from 'react';
import {FormGroup,
        Col,
        FormControl,
        ControlLabel} from 'react-bootstrap';

class Settings extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      room_id: ''
    };
  }

onRoomChange(e) {
    this.setState({room_id: e.target.value});
  }

  render() {
   let rooms = []
    this.props.sites.map((site) =>
      site.rooms.map((room) =>
        rooms.push({name: `${site.name}-${room.name}`, id: room.id})
      )
    );
    return (
      <div className="roomOption">
        <FormGroup controlId="room_id">
          <Col componentClass={ControlLabel} sm={2}>
            Room
            </Col>
            <Col sm={7}>
              <FormControl
                componentClass="select"
		        defaultValue={this.props.selectedRoom}
                onChange={this.onRoomChange.bind(this)}
                placeholder="select">
                  <option />
                  {rooms.map((room) => {
                    return <option
                      key={room.id}
                      value={room.id}>{room.name}</option>
                    })
                  }
              </FormControl>
            </Col>
        </FormGroup>
      </div>
    );
  }
}

export default Settings;
