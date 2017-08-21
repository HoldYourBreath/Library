import React from 'react';
import {Link} from 'react-router-dom';

class NavbarUserInfo extends React.Component {
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
          <li>
            <Link to='/add_book'>Add Book</Link>
          </li>
          <li>
            <Link to='/admin'>Admin</Link>
          </li>
          <li>
            <a href="/books" onClick={this.props.logOut}>Logout</a>
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
