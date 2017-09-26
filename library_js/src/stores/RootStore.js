import { types } from "mobx-state-tree";
import Room from "./Room";

const RootStore = types
.model({
  rooms: types.optional(types.map(Room), {}),
  selectedRoom: types.optional(types.number, 0)
})
.actions(self => {
  function fetchRooms() {
    console.log('FetchRooms');
  }
  function selectRoom(roomId, save=true) {
    self.selectedRoom = parseInt(roomId, 10);
    if (save) {
      localStorage.setItem('selectedRoom', roomId);
    }
  }
  function initStore() {
    let selectedRoom = localStorage.getItem('selectedRoom');
    if (selectedRoom) {
      self.selectRoom(selectedRoom);
    }
  }
  return { fetchRooms, initStore, selectRoom};
});

export default RootStore.create();
