import React from 'react';
import locationStore from '../stores/LocationStore';
import { observer } from 'mobx-react';
import {
  Form,
  Col,
  FormGroup,
  FormControl,
  ControlLabel
} from 'react-bootstrap';

class LocationSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  onRoomSelect(e) {
    locationStore.selectRoom(parseInt(e.target.value, 10));
  }
  render() {
    console.log(locationStore.selectedSite);
    return (
      <Form horizontal>
        <FormGroup controlId='locationFilter'>
          <Col componentClass={ControlLabel} sm={2}>
            Room
          </Col>
          <Col sm={3}>
            <FormControl 
              componentClass='select'
              value={localStorage.selectedRoom}
              onChange={this.onRoomSelect.bind(this)}
              placeholder='select'>
                <option key={0} value={0}/>
                  {locationStore.rooms.map((room, i) => {
                    return <option
                              key={i}
                              value={room.roomId}>
                              {room.roomName}
                            </option>
                  })}
            </FormControl>
          </Col>
          <Col componentClass={ControlLabel} sm={2}>
            Site
          </Col>
          <Col sm={3}>
            <FormControl 
              componentClass='select'
              value={localStorage.selectedSite}
              onChange={this.props.onSiteSelect.bind(this)}
              placeholder='select'>
                <option key={0} value={0}/>
                  {locationStore.sites.map((site, i) => {
                    return <option
                              key={i}
                              value={site.siteId}>
                              {site.siteName}
                            </option>
                  })}
            </FormControl>
          </Col>
        </FormGroup>
      </Form>
    )
  }
}

export default observer(LocationSelector);
