import React from 'react';
import {Link} from 'react-router-dom';

class NavbarUserInfo extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    if (!this.props.secret) {
      return (
        <ul className="nav navbar-nav navbar-right">
          <li>
            <Link to='/log_in'>
              Log in
            </Link>
          </li>
        </ul>
      );
    }
    return (
      <span>
        <ul className="nav navbar-nav navbar-right">
          <li>
            <a href="/logout">logout</a>
          </li>
        </ul>
        <p className="nav navbar-nav navbar-right navbar-text">Signed in as 
          <a className="navbar-link"> {this.props.signum}</a>
        </p>
      </span>
    );
  }
}

export default NavbarUserInfo;
