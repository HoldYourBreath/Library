import { types } from 'mobx-state-tree';
import {validateSession, deleteSessionApi, createSession} from '../lib/sessionApi';

const SessionStore = types
.model({
  secret: types.optional(types.string, ''),
  signum: types.optional(types.string, ''),
  session_id: types.optional(types.number, -1),
  loggedIn: types.optional(types.boolean, false)
})
.actions(self => {
  function initSession() {
    let session_id = localStorage.getItem('session_id');
    let secret = localStorage.getItem('secret');
    if (secret && session_id) {
      validateSession(session_id, secret)
      .then(() => {
          console.log("session valid");
          self.setSession(session_id, secret);
      })
      .catch((e) => {
        console.log("Invalid session!", e);
      });
    } else {
      console.log("No valid session!");
    }
  }

  function setSession(user, session_id, secret) {
    self.session_id = session_id;
    self.signum = user;
    self.secret = secret;
    self.loggedIn = true;
    localStorage.setItem('signum', user);
    localStorage.setItem('session_id', session_id);
    localStorage.setItem('secret', secret);
  }
  
  function validateUserSession(user, password, cb) {
    createSession(user, password)
    .then((res) => {
      self.setSession(user, res.session_id, res.secret);
      cb({
        session_id: res.session_id,
        secret: res.secret
      });
    })
    .catch((e) => {
      console.log("Failed to create session!");
    });
  }
  
  function deleteSession() {
    deleteSessionApi(self.session_id, self.secret)
    .then(() => {
      self.clearSession();
    });
  }

  function clearSession() {
    self.loggedIn = false;
    self.session_id = -1;
    self.secret = '';
    localStorage.removeItem('session_id');
    localStorage.removeItem('secret');
  }

  return { initSession, setSession, clearSession, validateUserSession, deleteSession };
});

export default SessionStore.create();
