import React from 'react';
import {deleteLoan} from '../lib/loans';
import {FormGroup, 
        Button, 
        Col,
        Alert,
        Form,
        FormControl, 
        ControlLabel} from 'react-bootstrap';
const request = require('superagent');
const FontAwesome = require('react-fontawesome');


class CheckInBook extends React.Component {
    constructor(props) {
    super(props);
    this.state = {
      errMsg: null,
      infoMsg: null,
      loadingUserData: false,
      bookId: ""
    };
  }

  onBookIdInput(e) {
    this.setState({bookId: e.target.value});
  }

  resetForms() {
    this.setState({
      errMsg: null,
      infoMsg: null,
      bookId: ""
    });
  }

  returnBook() {
    deleteLoan(this.state.bookId)
      .then((res) => {
        this.setState({infoMsg: 'Book successfully returned!'});
        this.resetForms();
      })
      .catch((e) => {
        this.setState({errorMsg: e});
      });
  }

  submitBookIdButtonPress() {
    //this.getBookData(this.state.bookId);
  }

  render() {
    console.log(this.state);
    return (
      <div>
        <h1>Return book</h1>
        {this.state.errorMsg ? 
          <Alert bsStyle="danger"><strong>{this.state.errorMsg}</strong></Alert> : null}
        {this.state.infoMsg ? 
          <Alert bsStyle="info"><strong>{this.state.infoMsg}</strong></Alert> : null}
        <Form horizontal>
          <FormGroup controlId="bookId">
            <Col 
              componentClass={ControlLabel} 
              sm={2}>
              Book Id
            </Col>
            <Col sm={3}>
              <FormControl
                value={this.state.bookId}
                onChange={this.onBookIdInput.bind(this)}
                type="text" 
                placeholder="123..." />
            </Col>
            <Button onClick={this.returnBook.bind(this)}>
              Return book
            </Button>
          </FormGroup>
        </Form>
      </div>
    );
  }
}

export default CheckInBook;