import { types } from 'mobx-state-tree';
import {validateSession, deleteSessionApi, createSession} from '../lib/sessionApi';

const SessionStore = types
.model({
  secret: types.optional(types.string, ''),
  signum: types.optional(types.string, ''),
  loggedIn: types.optional(types.boolean, false)
})
.actions(self => {
  function initSession() {
    let signum = localStorage.getItem('signum');
    let secret = localStorage.getItem('secret');
    if (secret && signum) {
      validateSession(signum, secret)
      .then(() => {
          console.log("session valid");
          self.setSession(signum, secret);
      })
      .catch((e) => {
        console.log("Invalid session!");
      });
    } else {
      console.log("No valid session!");
    }
  }

  function setSession(signum, secret) {
    self.signum = signum;
    self.secret = secret;
    self.loggedIn = true;
    localStorage.setItem('signum', signum);
    localStorage.setItem('secret', secret);
  }
  
  function validateUserSession(signum, password, cb) {
    createSession(signum, password)
    .then((res) => {
      self.setSession(res.signum, res.secret);
      cb({
        signum: res.signum,
        secret: res.secret
      });
    })
    .catch((e) => {
      console.log(e);
      console.log("Failed to create session!");
    });
  }
  
  function deleteSession() {
    deleteSessionApi(self.signum, self.secret)
    .then(() => {
      self.clearSession();
    });
  }

  function clearSession() {
    self.loggedIn = false;
    self.signum = '';
    self.secret = '';
    localStorage.removeItem('signum');
    localStorage.removeItem('secret');
  }

  return { initSession, setSession, clearSession, validateUserSession, deleteSession };
});

export default SessionStore.create();
