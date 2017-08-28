import React, { Component } from 'react';
import {FormGroup, 
        Button, 
        Col,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
import { Redirect } from 'react-router';
const request = require('superagent');

class LogIn extends Component {
    constructor(props) {
    super(props);
    this.state = {
      errMsg: null,
      signum: "",
      password: "",
      redirect: false
    };
  }

  authenticate() {
    let url = `${window.__appUrl}/api/login`;
    let signum = this.state.signum;
    request
      .post(url)
      .send({
        signum: signum,
        password: this.state.password
      })
      .type('application/json')
      .on('error', (err) => {
        this.setState({errorMsg: `Authentication failed`});
      })
      .end((err, res) => {
        if (!err) {
          this.setState({redirect: true});
          this.props.onAuthenticationDone({
            signum: signum,
            secret: res.body.secret
          });
         }
    });
  }

  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }

  render() {
    const ErrAlert = this.state.errorMsg ? <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null;
  if (this.state.redirect) {
    return <Redirect to={'/'}/>;
  }
    return (
      <div className="jumbotron">
        <Form horizontal>
          <FormGroup controlId="signum">
            <p>
            Login using your windows credentials
            </p>
          </FormGroup>
          {ErrAlert}
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
                Login
              </Button>
            </Col>
          </FormGroup>
        </Form>
      </div>
    );
  }
}

export default LogIn;