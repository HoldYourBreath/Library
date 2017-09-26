import { types } from "mobx-state-tree";


const Room = types
.model({
  roomId: types.optional(types.number, 0),
  roomName: types.optional(types.string, ""),
  siteName: types.optional(types.string, ""),
  siteId: types.optional(types.number, 0)
});

const Site = types
.model({
  siteName: types.optional(types.string, ""),
  siteId: types.optional(types.number, 0)
});

export { Room, Site };