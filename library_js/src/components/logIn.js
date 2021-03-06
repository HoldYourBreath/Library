import React, { Component } from 'react';
import {FormGroup, 
        Button, 
        Col,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
import { Redirect } from 'react-router';


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

  authenticate(e) {
    this.props.sessionStore.validateUserSession(
      this.state.signum,
      this.state.password,
      this.props.onAuthenticationDone);
    e.preventDefault();
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
        <Form horizontal onSubmit={this.authenticate.bind(this)}>
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
              <Button type="submit">
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