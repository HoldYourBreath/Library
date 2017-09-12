import React from 'react';
import {Link} from 'react-router-dom';
import {NavDropdown} from 'react-bootstrap';

class NavbarUserInfo extends React.Component {
  // eslint-disable-next-line
  constructor(props) {
    super(props);
  }
  logOut() {

  }
  render() {
    if (!this.props.secret) {
      return (
        <ul className="nav navbar-nav navbar-right">
          <li>
            <Link to='/login'>
              Log in
            </Link>
          </li>
        </ul>
      );
    }
    return (
      <span>
        <ul className="nav navbar-nav navbar-right">
          <NavDropdown eventKey={1} title="Admin" id="basic-nav-dropdown">
            <li>
              <Link to='/admin'>Sites and rooms</Link>
              <a href="/add_book" onClick=''>Add book</a>
            </li>
          </NavDropdown>
          <NavDropdown eventKey={2} title={this.props.signum} id="basic-nav-dropdown">
            <li>
              <Link to='/settings'>Settings</Link>
              <a href="/books" onClick={this.props.logOut}>Log out</a>
            </li>
          </NavDropdown>
        </ul>
      </span>
    );
  }
}

export default NavbarUserInfo;
