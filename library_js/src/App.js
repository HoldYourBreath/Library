import React from 'react';
import {getLocations} from './lib/sites';
import ListBooks from './components/ListBooks';
import LoanBook from './components/loan';
import LogIn from './components/logIn';
import AddBook from './components/addBook';
import AdminPage from './components/admin';
import SettingsPage from './components/settings';
import NavbarUserInfo from './components/navbar_user_info';
import './App.css';
import {
  withRouter,
  Route,
  Link
} from 'react-router-dom';
const request = require('superagent');

window.__appUrl = "http://127.0.0.1:5000";


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sites: [],
      redirectTo: '',
      selectedRoom: '',
      signum: '',
      secret: ''
    };
  }

  authenticationDone(sessionInfo) {
    const location = {
      pathname: this.state.redirectTo,
      state: {from: 'login'}
    }
    this.props.history.push(location);
    this.setState({
      signum: sessionInfo.signum,
      secret: sessionInfo.secret,
      redirectTo: ''
    });
    localStorage.setItem('signum', sessionInfo.signum);
    localStorage.setItem('secret', sessionInfo.secret);
  }

  onRoomSelection(roomId) {
    localStorage.setItem('selectedRoom', roomId);
    this.setState({selectedRoom: roomId});
  }

  updateLocations() {
    getLocations()
      .then((locations) => {
        this.setState({sites: locations});
    });
  }

  componentWillMount() {
    this.updateLocations();
    let selectedRoom = localStorage.getItem('selectedRoom');
    if (selectedRoom) {
      this.setState({selectedRoom: selectedRoom});
    }
    let signum = localStorage.getItem('signum');
    let secret = localStorage.getItem('secret');
    if (secret && signum) {
      // Validate stored session.
      request
        .post(`${window.__appUrl}/api/login/validate`)
        .send({signum: signum, secret: secret})
        .type('application/json')
        .end((err, res) => {
          if(err) {
            this.clearLocalStorage();
          } else {
            this.setState({signum: signum, secret: secret});
          }
        });
    }
  }
  clearLocalStorage() {
    localStorage.removeItem('signum');
    localStorage.removeItem('secret');
  }

  logOut(){
    let url = `${window.__appUrl}/api/login/delete`;
    request
      .post(url)
      .send({
        signum: this.state.signum,
        secret: this.state.secret
      })
      .type('application/json')
      .end((err, res) => {
        if (err) {
          console.error(err);
        }
        this.setState({
          signum: '',
          secret: ''
        });
        this.clearLocalStorage();
      });
  }
  logInBegun() {
    this.setState({redirectTo: this.props.location.pathname});
  }

  render() {
    return (
          <div>
          <nav className="navbar navbar-default">
            <div className="container-fluid">
              <div className="navbar-header">
                <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                  <span className="sr-only">Toggle navigation</span>
                  <span className="icon-bar"/>
                  <span className="icon-bar"/>
                  <span className="icon-bar"/>
                </button>
                <a className="navbar-brand" href='/brand'>Brand</a>
              </div>
              <div className="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                <ul className="nav navbar-nav">
                  <li>
                    <Link to='/books'>Books</Link>
                  </li>
                  <li>
                    <Link to='/loan'>Loan Book</Link>
                  </li>
                </ul>
                <NavbarUserInfo 
                  logInBegun={this.logInBegun.bind(this)}
                  logOut={this.logOut.bind(this)}
                  secret={this.state.secret} 
                  signum={this.state.signum}/>
              </div>
            </div>
          </nav>
          <div className='container'>
            <Route path={'/books'} component={ListBooks}/>
            <Route path={'/loan'} component={LoanBook}/>
            <Route
              path={'/add_book'}
              component={() => (<AddBook
                                  onRoomSelection={this.onRoomSelection.bind(this)}
                                  selectedRoom={this.state.selectedRoom}
                                  sites={this.state.sites} />)}/>
            <Route 
              path={'/admin'}
              component={() => (<AdminPage 
                                  locationUpdate={this.updateLocations.bind(this)}
                                  sites={this.state.sites} />)}/>
            <Route
              path={'/settings'}
              component={() => (<SettingsPage
                                  locationUpdate={this.updateLocations.bind(this)}
                                  sites={this.state.sites} />)}/>
            <Route 
              path={'/login'}
              component={() => (
                <LogIn 
                  onAuthenticationDone={this.authenticationDone.bind(this)} />)}/>
          </div>
        </div>
    );
  }
}

export default withRouter(App);
