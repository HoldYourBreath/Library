import React from 'react';

// TODO: Maybe have a green / red status indicator here?
const OnLoanStatus = ({status}) => (
  status ? <span>N/A</span> : <span>OK</span>
);

export default OnLoanStatus;
