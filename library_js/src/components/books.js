import React, { Component } from 'react';
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
      books: []
    };
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
    console.log(data);
    return (
      <div>
        <ReactTable
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
render(<Books />, document.getElementById("root"));
export default Books;
