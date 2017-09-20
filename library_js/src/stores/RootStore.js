import { types } from "mobx-state-tree";
import Room from "./Room";

const RootStore = types
.model({
  rooms: types.optional(types.map(Room), {}),
  selectedRoom: types.optional(types.number, 0),
  secret: types.optional(types.string, ''),
  signum: types.optional(types.string, ''),
  loggedIn: types.optional(types.boolean, false)
})
.actions(self => {
  function fetchRooms() {
    console.log('FetchRooms');
  }
  function initStore() {
    console.log('initStore');
  }
  function setSession(signum, secret) {
    self.signum = signum;
    self.secret = secret;
    localStorage.setItem('signum', signum);
    localStorage.setItem('secret', secret);
  }
  function clearSession() {
    self.loggedIn = false;
    self.signum = '';
    self.secret = '';
    localStorage.removeItem('signum');
    localStorage.removeItem('secret');
  }
  return { fetchRooms, initStore, setSession, clearSession };
});

export default RootStore.create();
