import React, { Component } from 'react';
import { Form } from 'react-bootstrap';
import { render } from "react-dom";
import { Tips } from "./Utils";
import './books.css';
import ReactTable from 'react-table'
import 'react-table/react-table.css'
const request = require('superagent');


class Books extends Component {
  constructor() {
    super();
    this.state = {
      books: [],
      loadingBookData: false,
      errorMsg: null,
      infoMsg: null,
      isbn: '',
      tag: null,
      title: '',
      author: '',
      description: '',
      format: '',
      pages: '',
      publication_date: '',
      thumbnail: ''
    };
  }


  getBookData(isbn) {
    let url = `${window.__appUrl}/api/books/goodreads/${isbn}`;
    this.setState({loadingBookData: true});
    request
      .get(url)
      .type('application/json')
      .on('error', (err) => {
        this.setState({
          errorMsg: `Unable to fetch book info for ${isbn}`,
          loadingBookData: false
        });
      })
      .end((err, res) => {
        if (err) {
          return;
        }
        this.setState({loadingBookData: false});
        this.setState({errorMsg: null});
        let state = Object.assign({}, res.body);
        state.pages = state.num_pages;
        state.isbn = isbn;
        delete state.num_pages;
        delete state.errorMsg;
        this.setState(state);
      });
   };


  componentWillMount() {
    console.log("Get books");
    ;
    request
      .get(`${window.__appUrl}/api/books`)
      .type('application/json')
      .end((err, res) => {
        this.setState({books: res.body});
      });
  }

  render() {
    const data = this.state.books;

    return (
    <div className="flex-container">
      <div className="bookTable">
        <ReactTable
          getTdProps={(state, rowInfo, column, instance) => {
            return {
              onClick: (e) => {
                  if (rowInfo.original !== null) {
                    let url = `${window.__appUrl}/api/books/goodreads/${rowInfo.original.isbn}`;
                    this.setState({loadingBookData: true});
                    request
                      .get(url)
                      .type('application/json')
                      .on('error', (err) => {
                        this.setState({
                          errorMsg: `Unable to fetch book info for ${rowInfo.original.isbn}`,
                          loadingBookData: false
                        });
                      })
                      .end((err, res) => {
                        if (err) {
                          return;
                        }
                        this.setState({loadingBookData: false});
                        this.setState({errorMsg: null});
                        let state = Object.assign({}, res.body);
                        state.pages = state.num_pages;
                        delete state.num_pages;
                        delete state.errorMsg;
                        this.setState(state);
                        }
                      );
                }
               }
              }
            }
          }
         data={data}
          columns={
          [
            {
              Header: "",
              columns:
              [
                {
                  Header: "Title",
                  accessor: "title",
                  minWidth: 200
                }
              ]
            },
            {
              Header: "",
              columns:
              [
                {
                  Header: "Published",
                  accessor: "publication_date",
                  width: 67
                }
              ]
            }
          ]}
          defaultPageSize={20}
          className="-striped -highlight"
        />
        <br />
        <Tips />
      </div>
      <div className="bookInfo">
      <Form horizontal>
        <div className="title">
          {this.state.title}
        </div>

        <div className="author">
          {this.state.author}    {this.state.format}    {this.state.pages}
        </div>

          <img id="" alt="" src={this.state.thumbnail} />

        <div className="description">
          {this.state.description}
        </div>
      </Form>
      </div>
    </div>
    );
  }
}
render(<Books />, document.getElementById("root"));
export default Books;
