import React from 'react';
import ShowThumbnail from './ShowThumbnail';
import sessionStore from '../stores/Session';
import { observer } from 'mobx-react';
import rootStore from '../stores/RootStore';
import { Redirect } from 'react-router'
import {FormGroup,
        Button, 
        Col,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';

        
const request = require('superagent');
const FontAwesome = require('react-fontawesome');

class AddBook extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loadingBookData: false,
      errorMsg: '',
      infoMsg: '',
      room_id: '',
      isbn: '',
      tag: '',
      title: '',
      authors: '',
      description: '',
      format: '',
      pages: '',
      publication_date: '',
      thumbnail: ''
    };
  }

  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }
  onIsbnChange(e) {
    this.setState({[e.target.id]: e.target.value});
    let isbn = e.target.value;
    if (isbn.length === 13) {
      this.getBookData(isbn);
    }
  }
  getBookData(isbn) {
    let url = `${window.__appUrl}/api/books/goodreads/${isbn}`;
    this.setState({loadingBookData: true});
    request
      .get(url)
      .type('application/json')
      .on('error', (err) => {
        this.setState({
          errorMsg: `Unable to fetch book info for ${isbn}`,
          loadingBookData: false
        });
      })
      .end((err, res) => {
        if (err) {
          return;
        }
        this.setState({loadingBookData: false});
        this.setState({errorMsg: null});
        let state = Object.assign({}, res.body);
        state.pages = state.num_pages;
        state.isbn = isbn;
        delete state.num_pages;
        delete state.errorMsg;
        this.setState(state);
      });
  }

  reset(e) {
    this.setState({
        loadingBookData: false,
        errorMsg: null,
        infoMsg: null,
        thumbnail: null,
        isbn: '',
        title: '',
        tag: '',
        authors: '',
        description: '',
        format: '',
        pages: '',
        publication_date: ''
     });
  }

  submitBook() {
    let url = `${window.__appUrl}/api/books/${this.state.tag}`;
    request
      .put(url)
      .send(this.state)
      .type('application/json')
      .on('error', (err) => {
        this.setState({errorMsg: `Unable to post new book: ${err.response.text}`});
      })
      .end((err, res) => {
        if (!err) {
          this.setState({
              errorMsg: null,
              infoMsg: `New book with tag ${res.body.tag} added!`,
            });
        }
      });
  }

  onRoomChange(e) {
    this.setState({room_id: e.target.value});
    rootStore.selectRoom(e.target.value);
  }

  render() {
    const ErrAlert = this.state.errorMsg ? <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null;
    const InfoAlert = this.state.infoMsg ? <Alert bsStyle="success"><strong>{this.state.infoMsg}</strong></Alert> : null;
    let rooms = []
    this.props.sites.map((site) =>
      site.rooms.map((room) =>
        rooms.push({name: `${site.name}-${room.name}`, id: room.id})
      )
    );
    if (!sessionStore.loggedIn) {
      return <Redirect to="/login" push={false} />      
    }
    return (
      <div>
        <h1>Add book</h1>
          {ErrAlert}
          {InfoAlert}
          <Form horizontal>
            <FormGroup controlId="isbn">
              <Col componentClass={ControlLabel} sm={2}>
                ISBN-13
              </Col>
              <Col sm={5}>
                <FormControl
                  value={this.state.isbn}
                  onChange={this.onIsbnChange.bind(this)}
                  type="text"
                  autoComplete="off"
                  placeholder=""/>
              </Col>
              <Col sm={1}>
                {this.state.loadingBookData ? <FontAwesome name='spinner' size='2x'spin/> : null}
              </Col>
            </FormGroup>
              <FormGroup controlId="tag">
              <Col componentClass={ControlLabel} sm={2}>
                TAG
              </Col>
              <Col sm={5}>
                <FormControl
                  value={this.state.tag}
                  onChange={this.onFormInput.bind(this)}
                  type="text"
                  autoComplete="off"
                  placeholder=""/>
              </Col>
            </FormGroup>
            <FormGroup controlId="title">
              <Col componentClass={ControlLabel} sm={2}>
                Title
              </Col>
              <Col sm={7}>
                <FormControl
                  value={this.state.title}
                  onChange={this.onFormInput.bind(this)}
                  type="text"
                  autoComplete="off"
                  placeholder=""/>
              </Col>
            </FormGroup>
            <FormGroup controlId="room_id">
              <Col componentClass={ControlLabel} sm={2}>
                Room
              </Col>
              <Col sm={7}>
                <FormControl 
                  componentClass="select"
		              defaultValue={rootStore.selectedRoom}
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
            <FormGroup controlId="authors">
              <Col componentClass={ControlLabel} sm={2}>
                Authors
              </Col>
              <Col sm={7}>
                <FormControl
                  value={this.state.authors}
                  onChange={this.onFormInput.bind(this)}
                  type="text"
                  autoComplete="off"
                  placeholder=""/>
              </Col>
            </FormGroup>
            <FormGroup controlId="description">
              <Col componentClass={ControlLabel} sm={2}>
                Description
              </Col>
              <Col sm={10}>
                <FormControl
                  value={this.state.description}
                  onChange={this.onFormInput.bind(this)}
                  style={{height: '150px'}}
                  componentClass="textarea"
                  autoComplete="off"
                  placeholder=""/>
              </Col>
            </FormGroup>
            <FormGroup controlId="format">
              <Col componentClass={ControlLabel} sm={2}>
                Format
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.format}
                  onChange={this.onFormInput.bind(this)}
                  autoComplete="off"
                  placeholder=""/>
              </Col>
              <Col componentClass={ControlLabel} sm={2}>
                Pages
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.pages}
                  onChange={this.onFormInput.bind(this)}
                  autoComplete="off"
                  placeholder=""/>
              </Col>
              <Col componentClass={ControlLabel} sm={2}>
                Publication date
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.publication_date}
                  onChange={this.onFormInput.bind(this)}
                  autoComplete="off"
                  placeholder=""/>
                  <br/>
              </Col>
            </FormGroup>
            <FormGroup controlId="publication_date">
              <Col componentClass={ControlLabel} sm={2}>
                Thumbnail
              </Col>
              <Col sm={6}>
                <ShowThumbnail thumbnailUrl={this.state.thumbnail}/>
              </Col>
            </FormGroup>
            <FormGroup>
              <Col smOffset={2} sm={1}>
                <Button
                  disabled={!this.state.isbn || !this.state.tag}
                  onClick={this.submitBook.bind(this)}>
                  Submit book
                </Button>
              </Col>
              <Col smOffset={2} sm={1}>
                <Button
                  onClick={this.reset.bind(this)}>
                  Reset
                </Button>
              </Col>
            </FormGroup>
          </Form>
        </div>
    );
  }
}

export default observer(AddBook);
