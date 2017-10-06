import { types } from 'mobx-state-tree';
import { getLocations, addSite, renameRoom } from '../lib/sites';
import {Room, Site} from "./Locations";

const LocationStore = types
.model({
  rooms: types.optional(types.array(Room), []),
  sites: types.optional(types.array(Site), []),
  selectedRoom: types.optional(types.number, 0),
  selectedSite: types.optional(types.number, 0)
})
.views(self => ({
}))
.actions(self => {
  function fetchRooms() {
    getLocations()
    .then((locations) => {
      let newRooms = [];
      let newSites = [];
      locations.forEach((site) => {
        newSites.push({
          siteName: site.name,
          siteId: site.id,
        });
        site.rooms.forEach((r) => {
          let newRoom = {
            roomId: r.id,
            roomName: r.name,
            siteId:  site.id,
            siteName: site.name
          }
          newRooms.push(newRoom);
        });
      });
      self.applyRooms(newRooms);
      self.applySites(newSites);
    });
  }
  function postRoomRename(siteId, roomId, roomName) {
    renameRoom(siteId, roomId, roomName)
    .then(() => {
      self.applyRenameRoom(roomId, roomName);
    });
  }
  function applyRenameRoom(roomId, roomName) {
    self.rooms.forEach((r) => {
      if (r.roomId === roomId)
        r.roomName = roomName;
    });
  }
  function applyRooms(rooms) {
    self.rooms = rooms;
  }
  function applySites(sites) {
    self.sites = sites;
  }
  function applyNewSite(siteName, siteId) {
    self.sites.push({
      siteId: siteId,
      siteName: siteName
    });
  }
  function postNewSite(siteName) {
    addSite(siteName)
    .then((newSite) => {
      self.applyNewSite(newSite.name, newSite.id);
    });
  }
  function selectRoom(roomId, save=true) {
    self.selectedRoom = parseInt(roomId, 10);
    if (save) {
      localStorage.setItem('selectedRoom', roomId);
    }
  }
  function selectSite(siteId, save=true) {
    self.selectedSite = parseInt(siteId, 10);
    if (save) {
      localStorage.setItem('selectedSite', siteId);
    }
  }
  function initStore() {
    let selectedRoom = localStorage.getItem('selectedRoom');
    let selectedSite = localStorage.getItem('selectedSite');
    if (selectedSite) {
      self.selectSite(selectedSite);
    }
    self.fetchRooms();
    if (selectedRoom) {
      self.selectRoom(selectedRoom);
    }
  }
  return { 
    fetchRooms, initStore, postRoomRename, applyRenameRoom, 
    selectRoom, applySites, applyRooms, 
    applyNewSite, postNewSite, selectSite
  };
});

export default LocationStore.create();
