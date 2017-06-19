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
    this.state = {
      loadingBookData: false,
      errorMsg: null,
      infoMsg: null,
      isbn: '',
      description: '',
      tag: '',
      pages: '',
      author: '',
      format: '',
      title: '',
      publication_date: ''
    };
  }
  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }
  onIsbnChange(e) {
    let isbn = e.target.value;
    if (isbn.length === 13) {
      console.log("onIsbnChange: " + isbn);
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
        console.log("error!!!");
        console.log("error!!!");
        console.log("error!!!");
        console.log(err);
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
              infoMsg: `New book with tag ${res.body.tag} added!`
            });
        } 
      });
  }
  onRoomChange(e) {
    this.setState({room_id: e.target.value});
  }
  render() {
    const ErrAlert = this.state.errorMsg ? <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null;
    const InfoAlert = this.state.infoMsg ? <Alert bsStyle="success"><strong>{this.state.infoMsg}</strong></Alert> : null;
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
                ISBN
              </Col>
              <Col sm={4}>
                <FormControl 
                  onChange={this.onIsbnChange.bind(this)}
                  type="text" 
                  placeholder="ISBN" />
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
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
                  placeholder="Unique tag"/>
              </Col>
            </FormGroup>
            <FormGroup controlId="tag">
              <Col componentClass={ControlLabel} sm={2}>
                Title
              </Col>
              <Col sm={7}>
                <FormControl
                  value={this.state.title}
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
                  placeholder="Title"/>
              </Col>
            </FormGroup>
            <FormGroup controlId="room_id">
              <Col componentClass={ControlLabel} sm={2}>
                Room
              </Col>
              <Col sm={7}>
                <FormControl 
                  componentClass="select"
                  onChange={this.onRoomChange.bind(this)}
                  placeholder="select">
                  <option key="0" value=""></option>
                  {
                    this.props.rooms.map((room) => {
                      return <option 
                               key={room.id} 
                               value={room.id}>{room.room_name}</option>
                    })
                  }
                </FormControl>
              </Col>
            </FormGroup>
            <FormGroup controlId="tag">
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
            <FormGroup controlId="desc">
              <Col componentClass={ControlLabel} sm={2}>
                Description
              </Col>
              <Col sm={10}>
                <FormControl
                  value={this.state.description}
                  onChange={this.onFormInput.bind(this)}
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
                Pub date
              </Col>
              <Col sm={2}>
                <FormControl
                  value={this.state.publication_date}
                  onChange={this.onFormInput.bind(this)}
                  placeholder=""/>
              </Col>
            </FormGroup>
            <FormGroup>
              <Col smOffset={2} sm={10}>
                <Button 
                  onClick={this.submitBook.bind(this)}>
                  Submit book
                </Button>
              </Col>
            </FormGroup>
          </Form>;
        </div>
    );
  }
}

export default AddBook;