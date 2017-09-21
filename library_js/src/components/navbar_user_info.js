import React from 'react';
import {Link} from 'react-router-dom';
import {LinkContainer} from 'react-router-bootstrap';
import {NavDropdown, MenuItem} from 'react-bootstrap';
import { observer } from "mobx-react";


class NavbarUserInfo extends React.Component {
  logOut(e) {
    e.preventDefault();
    this.props.sessionStore.deleteSession();
  }

  render() {
    console.log('NavbarUserInfo', this.props.sessionStore.secret)
    if (!this.props.sessionStore.secret) {
      return (
        <ul className="nav navbar-nav navbar-right">
          <li>
            <Link 
              to="/login"
              onClick={this.props.logInBegun.bind(this)}>
              Log in
            </Link>
          </li>
        </ul>
      );
    }
   
    return (
      <span>
        <ul className="nav navbar-nav navbar-right">
          <NavDropdown eventKey={2} title="Admin" id="basic-nav-dropdown">
            <LinkContainer to='/admin'>
              <MenuItem eventKey={2.1}>Sites and rooms</MenuItem>
            </LinkContainer>
            <LinkContainer to="/add_book">
              <MenuItem eventKey={2.2}>Add book</MenuItem>
            </LinkContainer>
          </NavDropdown>
          <NavDropdown eventKey={3} title={this.props.sessionStore.signum} id="basic-nav-dropdown">
              <LinkContainer to='/settings'>
                <MenuItem eventKey={3.1}>Settings</MenuItem>
              </LinkContainer >
              <LinkContainer to="/books" onClick={this.logOut.bind(this)}>
                <MenuItem eventKey={3.2}>Log out</MenuItem>
              </LinkContainer>
          </NavDropdown>
        </ul>
      </span>
    );
  }
}

export default observer(NavbarUserInfo);
