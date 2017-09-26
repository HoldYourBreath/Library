
import React from 'react';
import locationStore from '../../stores/LocationStore';
import { observer } from 'mobx-react';
import {
  InputGroup,
  Glyphicon,
  Button,
  Alert,
  FormControl
} from 'react-bootstrap';
import { removeRoom } from '../../lib/sites';

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
    if (window.confirm('Are you sure you want to delete this room?') === true) {
    removeRoom(this.props.site_id, this.props.room.id)
      .then(() => {
          //his.props.locationUpdate();
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
      locationStore.postRoomRename(this.props.room.siteId, this.props.room.roomId, this.state.newRoomName);
    }
    this.setState({edit: false});
  }
  
  render () {
    const ErrAlert = this.state.errorMsg ? <Alert bsStyle='danger'><strong>{this.state.errorMsg}</strong></Alert> : null;
    if (this.state.edit) {
      return (
        <InputGroup>
          {ErrAlert}
          <FormControl
            type='text'
            defaultValue={this.props.room.roomName}
            onChange={this.handleNewNameChange.bind(this)} />
          <InputGroup.Button>
            <Button onClick={this.handleRemoveRoom.bind(this)}>
              <Glyphicon title='Remove room' glyph='remove' style={{color: 'red'}} />
            </Button>
            <Button onClick={this.handleRenameRoom.bind(this)}>
              <Glyphicon title='Submit change' glyph='ok' style={{color: 'green'}} />
            </Button>
          </InputGroup.Button>
        </InputGroup>
      )
    } else {
      return (
        <li className='list-group-item'>
          {this.props.room.roomName}
          <a
            role='button'
            className='input-group-button'
            onClick= {this.toggleEdit.bind(this)}>
            <span
              className='glyphicon glyphicon-pencil pull-right'
              style={{color: 'gold'}}/>
          </a>
        </li>
      )
    }
  }
}

export default observer(Room);
