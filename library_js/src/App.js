import React, { Component } from 'react';
import logo from './logo.svg';
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
      signum: '',
      sessionSecret: ''
    };
  }

  authenticationDone(sessionInfo) {
    console.log(sessionInfo);
    this.setState({
      signum: sessionInfo.signum,
      sessionSecret: sessionInfo.secret
    });
  }

  componentWillMount() {
    request
      .get(`${window.__appUrl}/api/rooms`)
      .type('application/json')
      .end((err, res) => {
        if (err) {
          console.error(err);
          return;
        }
        this.setState({rooms: res.body});
      });
  }
  logOut(){
    console.log("logout");
    this.setState({
      signum: '',
      sessionSecret: ''
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
                  secret={this.state.sessionSecret} 
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
