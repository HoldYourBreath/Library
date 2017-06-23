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


class LogIn extends Component {
    constructor(props) {
    super(props);
    this.state = {
      errMsg: null,
      signum: "",
      password: ""
    };
  }

  authenticate() {
    let url = `${window.__appUrl}/api/books/${this.state.tag}`;
    request
      .post(url)
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
  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }

  render() {
    console.log(this.state);
    return (
      <div className="jumbotron">
        <Form horizontal>
          <FormGroup controlId="signum">
            <p>
            Login using your windows credentials
            </p>
          </FormGroup>
          <FormGroup controlId="signum">
            <Col componentClass={ControlLabel} sm={2}>
            Signum
            </Col>
            <Col sm={10}>
              <FormControl
                value={this.state.signum}
                onChange={this.onFormInput.bind(this)}
                type="text" 
                placeholder="Signum" />
            </Col>
          </FormGroup>
          <FormGroup controlId="password">
            <Col componentClass={ControlLabel} sm={2}>
              Password
            </Col>
            <Col sm={10}>
              <FormControl 
                value={this.state.password}
                onChange={this.onFormInput.bind(this)}
                type="password" 
                placeholder="password"/>
            </Col>
          </FormGroup>
          <FormGroup>
            <Col smOffset={2} sm={10}>
              <Button onClick={this.authenticate.bind(this)}>
                Sign in
              </Button>
            </Col>
          </FormGroup>
        </Form>
      </div>
    );
  }
}

export default LogIn;