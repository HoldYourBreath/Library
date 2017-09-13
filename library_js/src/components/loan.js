import React from 'react';
import UserInfo from "./UserInfo";
import {FormGroup, 
        Button, 
        Col,
        Row,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
const request = require('superagent');
const FontAwesome = require('react-fontawesome');


class LoanBook extends React.Component {
    constructor(props) {
    super(props);
    this.state = {
      errMsg: null,
      userData: null,
      bookData: null,
      bookTitle: null,
      loadingUserData: false,
      userId: "",
      bookId: ""
    };
  }

  onFormInput(e) {
    this.setState({[e.target.id]: e.target.value});
  }

  getBookData(bookId) {
      this.setState({loadingBookData: true});
      let url = `${window.__appUrl}/api/books/${bookId}`;
      request
        .get(url)
        .type('application/json')
        .on('error', (err) => {
          console.log(err);
          this.setState({
            errorMsg: `Unable to get book: ${bookId}`,
            loadingBookData: false
          });
      })
      .end((err, res) => {
        this.setState({loadingBookData: false});
        if (!err) {
          this.setState({errorMsg: "",
                         bookData: res.body});
        }
      });
  }

  getUserData(userId) {
    this.setState({loadingUserData: true});
    let url = `${window.__appUrl}/api/user/${userId}`;
    request
      .get(url)
      .type('application/json')
      .on('error', (err) => {
        this.setState({
          errorMsg: `Unable to fetch user data for ${userId}`,
          loadingUserData: false
        });
      })
      .end((err, res) => {
        if (err) {
          let errMsg = null;
          if(err.status === 404) {
            errMsg = `User id ${userId} not found`;
          }
          this.setState({
            errorMsg: errMsg,
            userData: null});
          return;
        }
        this.setState({
          errorMsg: null,
          loadingUserData: false,
          userData: res.body
        });
      });
  }
  
  getUserDataButtonPress() {
    this.getUserData(this.state.userId);
  }

  loanBookButtonPress() {
    console.log("Loan book!");
  }
  getBookDataButtonPress() {
    this.getBookData(this.state.bookId);
  }
  render() {
    return (
      <div>
        <h1>
            Loan book
        </h1>
        {this.state.errorMsg ? 
          <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null}
        <Form horizontal>
            <FormGroup controlId="userId">
              <Col 
                componentClass={ControlLabel} 
                sm={2}>
                User Id
              </Col>
              <Col sm={3}>
                <FormControl
                  value={this.state.userId}
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
                  placeholder="123..." />
              </Col>
              <Col sm={1}>
                <Button onClick={this.getUserDataButtonPress.bind(this)}>
                  Get User
                </Button>
              </Col>
              <Col sm={1}>
                {this.state.loadingUserData ? <FontAwesome name='spinner' size='2x'spin/> : null}
              </Col>
            </FormGroup>
            <FormGroup controlId="bookId">
              <Col 
                componentClass={ControlLabel} 
                sm={2}>
                Book Tag
              </Col>
              <Col sm={3}>
                <FormControl
                  value={this.state.bookId}
                  onChange={this.onFormInput.bind(this)}
                  type="text" 
                  placeholder="456..." />
              </Col>
              <Col sm={1}>
                <Button onClick={this.getBookDataButtonPress.bind(this)}>
                  Get Book
                </Button>
              </Col>
              <Col sm={1}>
                {this.state.loadingBookData ? <FontAwesome name='spinner' size='2x'spin/> : null}
              </Col>
            </FormGroup>
          <FormGroup>
            <Col sm={6}/>
            <Col sm={6}>
            </Col>
          </FormGroup>
          <Row>
            <Col sm={6}>
              {this.state.userData ? <UserInfo userData={this.state.userData}/> : null}
            </Col>
            <Col sm={6}>
            </Col>
          </Row>
          <FormGroup>
            <Col sm={2}/>
            <Col sm={10}>
              {this.state.userData ? 
                <Button onClick={this.loanBookButtonPress.bind(this)}>Loan</Button> : null}
            </Col>
          </FormGroup>
        </Form>
      </div>
    );
  }
}

export default LoanBook;