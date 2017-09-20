import { types } from "mobx-state-tree";


const Room = types
.model({
  roomId: types.optional(types.number, 0),
  roomName: types.optional(types.string, "")
});

export default Room;