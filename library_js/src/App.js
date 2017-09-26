import React from 'react';
import sessionStore from './stores/Session';
import locationStore from './stores/LocationStore';
import ListBooks from './components/ListBooks';
import LoanBook from './components/loan';
import LogIn from './components/logIn';
import AddBook from './components/addBook';
import AdminPage from './components/Admin/';
import SettingsPage from './components/settings';
import NavbarUserInfo from './components/navbar_user_info';
import './App.css';
import {
  withRouter,
  Route,
  Link
} from 'react-router-dom';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      redirectTo: ''
    };
  }

  authenticationDone(sessionInfo) {
    const location = {
      pathname: this.state.redirectTo,
      state: {from: 'login'}
    }
    this.props.history.push(location);
  }

  updateLocations() {

  }

  componentWillMount() {
    sessionStore.initSession();
    locationStore.initStore();
  }

  logInBegun() {
    this.setState({redirectTo: this.props.location.pathname});
  }

  render() {
    return (
          <div>
          <nav className='navbar navbar-default'>
            <div className='container-fluid'>
              <div className='navbar-header'>
                <button type='button' className='navbar-toggle collapsed' data-toggle='collapse' data-target='#bs-example-navbar-collapse-1' aria-expanded='false'>
                  <span className='sr-only'>Toggle navigation</span>
                  <span className='icon-bar'/>
                  <span className='icon-bar'/>
                  <span className='icon-bar'/>
                </button>
                <a className='navbar-brand' href='/brand'>Brand</a>
              </div>
              <div className='collapse navbar-collapse' id='bs-example-navbar-collapse-1'>
                <ul className='nav navbar-nav'>
                  <li>
                    <Link to='/books'>Books</Link>
                  </li>
                  <li>
                    <Link to='/loan'>Loan Book</Link>
                  </li>
                </ul>
                <NavbarUserInfo
                  sessionStore={sessionStore}
                  logInBegun={this.logInBegun.bind(this)}/>
              </div>
            </div>
          </nav>
          <div className='container'>
            <Route path={'/books'} component={() => (
              <ListBooks
                rooms={this.state.sites}
              />)}/>
            <Route path={'/loan'} component={LoanBook}/>
            <Route
              path={'/add_book'}
              component={AddBook}/>
            <Route 
              path={'/admin'}
              component={AdminPage}/>
            <Route
              path={'/settings'}
              component={SettingsPage}/>
            <Route 
              path={'/login'}
              component={() => (
                <LogIn 
                  sessionStore={sessionStore}
                  onAuthenticationDone={this.authenticationDone.bind(this)} />)}/>
          </div>
        </div>
    );
  }
}

export default withRouter(App);
