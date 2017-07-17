import React from 'react';
import {FormGroup, 
        Button, 
        Col,
        Row,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
import {addSite, renameSite} from '../lib/sites';


class AdminPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedSiteId: ''
    }
  }
  renameSite() {
      let newSiteName = window.prompt('Enter new site name');
      if (newSiteName) {
        renameSite(this.state.selectedSiteId, newSiteName)
          .then(() => {
            this.props.locationUpdate();
        });
      }
  }

  addNewSite() {
    let newSite = window.prompt('Enter name of new site');
    if (newSite){
      addSite(newSite)
        .then(() => {
          this.props.locationUpdate();
        });
    }
  }

  siteSelected(e) {
    this.setState({selectedSiteId: parseInt(e.target.value)});
  }

  render() {
    let rooms = [];
    if (this.state.selectedSiteId !== 0) {
      rooms = this.props.rooms.filter(r => r.id === this.state.selectedSiteId);
    }
    return (
      <div>
        <h1>Admin</h1>
        <Row style={{paddingBottom: "25px"}}>
          <Col sm={3}/>
          <Col sm={3}>
            <Button 
              onClick={this.renameSite.bind(this)}>
              Rename site
            </Button>
            <Button style={{marginLeft: "25px"}} 
                    onClick={this.addNewSite.bind(this)}>
              Add site
            </Button>
          </Col>
          <Col sm={3}/>
          <Col sm={3}/>
        </Row>
        <Row>
          <Col sm={3}/>
          <Col sm={3}>
            <FormGroup controlId="siteSelect">
              <ControlLabel>Site</ControlLabel>
              <FormControl 
                componentClass="select" 
                onChange={this.siteSelected.bind(this)}
                placeholder="select">
                <option value="0">Select a site</option>
                {this.props.sites.map((site) => {
                  return (
                      <option 
                        key={site.id}
                        value={site.id}>{site.site_name}</option>
                  )
                })}
              </FormControl>
            </FormGroup>
          </Col>
          <Col sm={3}>
            <FormGroup controlId="roomSelect">
              <ControlLabel>Rooms</ControlLabel>
              <FormControl componentClass="select" placeholder="select">
                {rooms.map((room) => {
                  return (
                      <option 
                        key={room.id}
                        value={room.id}>{room.room_name}</option>
                  )
                })}
              </FormControl>
            </FormGroup>
          </Col>
          <Col sm={3}/>
        </Row>
      </div>
    );
  }
}

export default AdminPage;
