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


class LoanBook extends Component {
    constructor(props) {
    super(props);
    this.state = {
      errMsg: null,
      userName: null,
      bookTitle: null,
      loadingUserData: false,
      userId: "",
      bookId: ""
    };
  }

  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }

  getBookData(bookId) {
      this.setState({loadingBookData: true});
      let url = `${window.__appUrl}/api/books/${bookId}`;
      request
        .get(url)
        .type('application/json')
        .on('error', (err) => {
          console.log(err);
          this.setState({
            errorMsg: `Unable to get book: ${bookId}`,
            loadingBookData: false
          });
      })
      .end((err, res) => {
        this.setState({loadingBookData: false});
        if (!err) {
          this.setState({errorMsg: "",
                         bookTitle: res.body.title});
        }
        console.log(res);
        //this.setState({userName: res.body.name});
      });
  }


  getUserData(userId) {
    this.setState({loadingUserData: true});
    let url = `${window.__appUrl}/api/user/${userId}`;
    request
      .get(url)
      .type('application/json')
      .on('error', (err) => {
        this.setState({
          errorMsg: `Unable to fetch user data for ${userId}`,
          loadingUserData: false
        });
      })
      .end((err, res) => {
        this.setState({loadingUserData: false});
        if (!err) {
          this.setState({errorMsg: null,
                         userName: null});
          return;
        }
        console.log(res);
        this.setState({userName: res.body.name});
      });
  }
  
  getUserDataButtonPress() {
    this.getUserData(this.state.userId);
  }
  getBookDataButtonPress() {
    this.getBookData(this.state.bookId);
  }
  render() {
    return (
      <div>
        <h1>
            Loan book
        </h1>
        {this.state.errorMsg ? 
          <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null}
        <Form horizontal>
            <FormGroup controlId="userId">
              <Col 
                componentClass={ControlLabel} 
                sm={2}>
                User Id
              </Col>
              <Col sm={3}>
                <FormControl
                  value={this.state.userId}
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
                  placeholder="123..." />
              </Col>
              <Col sm={1}>
                <Button onClick={this.getUserDataButtonPress.bind(this)}>
                  Get User
                </Button>
              </Col>
              <Col sm={1}>
                {this.state.loadingUserData ? <FontAwesome name='spinner' size='2x'spin/> : null}
              </Col>
            </FormGroup>
            <FormGroup controlId="bookId">
              <Col 
                componentClass={ControlLabel} 
                sm={2}>
                Book Id
              </Col>
              <Col sm={3}>
                <FormControl
                  value={this.state.bookId}
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
                  placeholder="456..." />
              </Col>
              <Col sm={1}>
                <Button onClick={this.getBookDataButtonPress.bind(this)}>
                  Get Book
                </Button>
              </Col>
              <Col sm={1}>
                {this.state.loadingBookData ? <FontAwesome name='spinner' size='2x'spin/> : null}
              </Col>
            </FormGroup>
          <FormGroup>
            <Col sm={2}></Col>
            <Col sm={6}>
              <Alert bsStyle="info">
                <p><strong>Holy guacamole!</strong> Best check yo self, you're not looking too good.</p>
                <p><strong>Holy guacamole!</strong> Best check yo self, you're not looking too good.</p>
              </Alert>
            </Col>
          </FormGroup>
          <FormGroup>
            <Col sm={2}></Col>
            <Col sm={6}>
              <Button onClick={this.getUserDataButtonPress.bind(this)}>
                Loan
              </Button>
            </Col>
          </FormGroup>
        </Form>
      </div>
    );
  }
}

export default LoanBook;