import React from 'react';
import OnLoanStatus from './OnLoanStatus';


class TableRow extends React.Component {
    constructor() {
      super();
      this.state = {

      };
    };
    render() {
        return (
          <tr>
            <td><OnLoanStatus status={this.props.bookData.loaned}/></td>
            <td>{this.props.bookData.authors}</td>
            <td>{this.props.bookData.title}</td>
            <td>{this.props.bookData.isbn}</td>
          </tr>
        )
      }
}

export default TableRow;
