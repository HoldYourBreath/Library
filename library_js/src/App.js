import React, { Component } from 'react';
import logo from './logo.svg';
import {getLocations} from './lib/sites';
import Books from './components/books';
import LoanBook from './components/loan';
import LogIn from './components/logIn';
import AddBook from './components/addBook';
import AdminPage from './components/admin';
import NavbarUserInfo from './components/navbar_user_info';
import './App.css';
import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom';
const request = require('superagent');

window.__appUrl = "http://127.0.0.1:5000";


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      rooms: [],
      sites: [],
      signum: '',
      secret: ''
    };
  }

  authenticationDone(sessionInfo) {
    console.log(sessionInfo);
    this.setState({
      signum: sessionInfo.signum,
      secret: sessionInfo.secret
    });
    localStorage.setItem('signum', sessionInfo.signum);
    localStorage.setItem('secret', sessionInfo.secret);
  }

  updateLocations() {
    getLocations().
      then((locations) => {
        console.log(locations);
        this.setState({rooms: locations.rooms,
                       sites: locations.sites});
    });
  }

  componentWillMount() {
    this.updateLocations();
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

  render() {
    return (
      <Router>
          <div>
          <nav className="navbar navbar-default">
            <div className="container-fluid">
              <div className="navbar-header">
                <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                  <span className="sr-only">Toggle navigation</span>
                  <span className="icon-bar"></span>
                  <span className="icon-bar"></span>
                  <span className="icon-bar"></span>
                </button>
                <a className="navbar-brand" href="#">Brand</a>
              </div>
              <div className="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                <ul className="nav navbar-nav">
                  <li>
                    <Link to='/'>
                      Books
                    </Link>
                  </li>
                  <li>
                    <Link to='/loan'>
                      Loan Book
                    </Link>
                  </li>
                </ul>
                <NavbarUserInfo 
                  logOut={this.logOut.bind(this)}
                  secret={this.state.secret} 
                  signum={this.state.signum}/>
              </div>
            </div>
          </nav>
          <div className='container'>
            <Route exact path={'/'} component={Books}/>
            <Route path={'/loan'} component={LoanBook}/>
            <Route 
              path={'/add_book'}
              component={() => (<AddBook rooms={this.state.rooms} />)}/>
            <Route 
              path={'/admin'}
              component={() => (<AdminPage 
                                  rooms={this.state.rooms}
                                  locationUpdate={this.updateLocations.bind(this)}
                                  sites={this.state.sites} />)}/>
            <Route 
              path={'/log_in'}
              component={() => (
                <LogIn 
                  onAuthenticationDone={this.authenticationDone.bind(this)} />)}/>
          </div>
        </div>
      </Router>
    );
  }
}

export default App;
