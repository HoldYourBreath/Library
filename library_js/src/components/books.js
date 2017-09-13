import React from 'react';
import { Form } from 'react-bootstrap';
import { render } from "react-dom";
import { Tips } from "./Utils";
import ReactTable from 'react-table'
import 'react-table/react-table.css'
import '../App.css';
const request = require('superagent');


class Books extends React.Component {
  constructor() {
    super();
    this.state = {
      books: [],
      loadingBookData: false,
      errorMsg: '',
      infoMsg: '',
      isbn: '',
      tag: '',
      title: '',
      author: '',
      description: '',
      format: '',
      pages: '',
      publication_date: '',
      thumbnail: ''
    };
  };

  componentWillMount() {
    request
      .get(`${window.__appUrl}/api/books`)
      .type('application/json')
      .end((err, res) => {
        let currentBooks = res ? res.body : [];
        this.setState({books: currentBooks});
      });
  }

  bookSelected(bookData) {
    this.setState({
      description: bookData.description,
      authors: bookData.authors,
      format: bookData.format,
      pages: bookData.pages,
      title: bookData.title,
      thumbnail: bookData.thumbnail,
    });
  }

  render() {
    console.log(this.state.books);
    return (
    <div className="flex-container">
      <div className="bookTable">
        <ReactTable
          getTdProps={(state, rowInfo, column, instance) => {
            return {
              onClick: (e) => {
                if (rowInfo.original !== null) {
                  this.bookSelected(rowInfo.original);
                }
               }
              }
            }
          }
         data={this.state.books}
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
        <div className="booksTitle">
          {this.state.title}
        </div>

        <div className="booksAuthor">
          {this.state.authors}    {this.state.format}    {this.state.pages}
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

export default Books;
