import React from 'react';
import sessionStore from '../../stores/Session';
import locationStore from '../../stores/LocationStore';
import { Redirect } from 'react-router'
import Sites from './Sites';
import { observer } from 'mobx-react';


class AdminPage extends React.Component {
  render() {
    if (!sessionStore.loggedIn) {
      return <Redirect to="/login" push={false} />      
    }
    return (
      <div>
        <h1>Sites and rooms</h1>
        <p>Add sites, rename sites and add rooms to sites</p>
        <Sites sites={locationStore.sites}/>
      </div>
    );
  }
}

export default observer(AdminPage);
