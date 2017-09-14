import React from 'react';

const UserInfo = ({userData}) => (
  <div>
    <div style={{fontWeight: 'bold'}}>User Info:</div>
    <div>Name: {userData.name}</div>
    <div>Id: {userData.id}</div>
    <div>Email: {userData.email}</div>
  </div>
);

export default UserInfo;