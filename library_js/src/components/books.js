import React, { Component } from 'react';
import { Tips } from "./Utils";
import './books.css';
import ReactTable from 'react-table'
import 'react-table/react-table.css'
const request = require('superagent');


class Books extends Component {
  constructor() {
    super();
    this.state = {
      books: []
    };
  };

  componentWillMount() {
    console.log("Get books");
    request
      .get(`${window.__appUrl}/api/books`)
      .type('application/json')
      .end((err, res) => {
        let currentBooks = res ? res.body : [];
        this.setState({books: currentBooks});
      });
  }

  render() {
    return (
      <div>
        <ReactTable
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
                  Header: "Authors",
                  accessor: "authors"
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
                  width: 90
                }
              ]
            },
            {
              Header: '',
              columns:
              [
                {
                  Header: "Pages",
                  accessor: "pages",
                  width: 50
                }
              ]
            }
          ]}
          defaultPageSize={15}
          className="-striped -highlight"
        />
        <br />
        <Tips />
      </div>
    );
  }
}

export default Books;
