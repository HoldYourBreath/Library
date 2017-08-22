import React, { Component } from 'react';
import {FormGroup,
        Button, 
        Col,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
const request = require('superagent');
const FontAwesome = require('react-fontawesome');

class AddBook extends Component {
  constructor(props) {
    super(props);
    let room_id = localStorage.getItem('selected_room');
    if (room_id != null) {
      this.setState({room_id: room_id});
    }
    this.state = {
      loadingBookData: false,
      errorMsg: null,
      infoMsg: null,
      isbn: null,
      tag: null,
      title: null,
      author: null,
      description: null,
      format: null,
      pages: null,
      publication_date: null,
      thumbnail: 'https://images.gr-assets.com/books/1419180921s/23232941.jpg'
    };
  }
  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }
  onIsbnChange(e) {
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
        isbn: '',
        title: '',
        tag: '',
        author: '',
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
    localStorage.setItem('selected_room', e.target.value);
  }
  render() {
    const ErrAlert = this.state.errorMsg ? <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null;
    const InfoAlert = this.state.infoMsg ? <Alert bsStyle="success"><strong>{this.state.infoMsg}</strong></Alert> : null;
	let rooms = []
	this.props.sites.map((site) => {
		site.rooms.map((room) => {
			rooms.push({name: `${site.name}-${room.name}`, id: room.id});
		})
	});
    return (
      <div>
        <h1>Add book</h1>
          {ErrAlert}
          {InfoAlert}
          <Form horizontal>
            <FormGroup controlId="isbn">
              <Col 
                componentClass={ControlLabel} 
                sm={2}>
                ISBN-13
              </Col>
              <Col sm={4}>
                <FormControl
                  value={this.state.isbn}
                  onChange={this.onIsbnChange.bind(this)}
                  type="text" 
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
		          defaultValue={localStorage.getItem('selected_room')}
                  onChange={this.onRoomChange.bind(this)}
                  placeholder="select">
                    <option />
                    {
                      rooms.map((room) => {
                        return <option
                                 key={room.id}
                                 value={room.id}>{room.name}</option>
				      })
                    }
                </FormControl>
              </Col>
            </FormGroup>
            <FormGroup controlId="author">
              <Col componentClass={ControlLabel} sm={2}>
                Author
              </Col>
              <Col sm={7}>
                <FormControl
                  value={this.state.author}
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
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
                  placeholder=""/>
              </Col>
            </FormGroup>
            <FormGroup controlId="media">
              <Col componentClass={ControlLabel} sm={2}>
                Format
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.format}
                  onChange={this.onFormInput.bind(this)}
                  placeholder=""/>
              </Col>
              <Col componentClass={ControlLabel} sm={2}>
                Pages
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.pages}
                  onChange={this.onFormInput.bind(this)}
                  placeholder=""/>
              </Col>
              <Col componentClass={ControlLabel} sm={2}>
                Publication date
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.publication_date}
                  onChange={this.onFormInput.bind(this)}
                  placeholder=""/>
                  <br/>
              </Col>

               <Col componentClass={ControlLabel} sm={2}>
                Thumbnail
              </Col>
              <Col xs={6} md={3}>
                <img id="thumbnail" alt="thumbnail" src={this.state.thumbnail} />
              </Col>
            </FormGroup>
            <FormGroup>
              <Col smOffset={2} sm={1}>
                <Button
                  disabled={!this.state.isbn}
                  disabled={!this.state.tag}
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

export default AddBook;
