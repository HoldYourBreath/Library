import React from 'react';
import locationStore from '../stores/LocationStore';
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
  render() {
    return (
      <Form horizontal>
        <FormGroup controlId='locationFilter'>
          <Col componentClass={ControlLabel} sm={2}>
            Room
          </Col>
          <Col sm={3}>
            <FormControl 
              componentClass='select'
              onChange={this.props.onRoomChange.bind(this)}
              placeholder='select'>
                <option key={0} value={0}/>
                  {locationStore.rooms.map((room) => {
                    return <option
                              key={room.roomId}
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
              onChange={this.props.onSiteChange.bind(this)}
              placeholder='select'>
                <option key={0} value={0}/>
                  {locationStore.sites.map((site) => {
                    return <option
                              key={site.siteId}
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

export default LocationSelector;
