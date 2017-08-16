
const request = require('superagent');


const renameSite = function(siteId, newName) {
  return new Promise((resolve, reject) => {
    request
      .put(`${window.__appUrl}/api/sites/${siteId}`)
      .send({name: newName})
      .type('application/json')
      .end((err, res) => {
        if (err) {
          reject(err);
        } else {
          resolve(res.body);
        }
      });
  });
};

const getRooms = function() {
  return new Promise((resolve, reject) => {
    request
      .get(`${window.__appUrl}/api/rooms`)
      .type('application/json')
      .end((err, res) => {
        if (err) {
          reject(err);
        } else {
          resolve(res.body);
        }
      });
  });
};

const getLocations = () => {
  return new Promise((resolve, reject) => {
    request
      .get(`${window.__appUrl}/api/sites`)
      .type('application/json')
      .end((err, res) => {
        if (err) {
          reject(err);
        } else {
          resolve(res.body);
        }
      });
  });
};

const addSite = (siteName) => {
  return new Promise((resolve, reject) => {
    request
      .post(`${window.__appUrl}/api/sites`)
      .send({name: siteName})
      .type('application/json')
      .end((err, res) => {
        if (err) {
          reject(err);
        } else {
          resolve(res.body);
        }
      });
  });
};

const addRoom = (siteId, siteName) => {
  return new Promise((resolve, reject) => {
    request
	  .post(`${window.__appUrl}/api/sites/${siteId}/rooms`)
	  .send({name: siteName})
	  .type('application/json')
	  .end((err, res) => {
		  if (err) {
			  reject(err);
		  } else {
			  resolve(res.body);
		  }
	  });
  });
};

const renameRoom = (siteId, roomId, newName) => {
  return new Promise((resolve, reject) => {
    request
      .put(`${window.__appUrl}/api/sites/${siteId}/rooms/${roomId}`)
      .send({name: newName})
      .type('application/json')
      .end((err, res) => {
        if (err) {
          reject(err);
        } else {
          resolve(res.body);
        }
      });
  });
};

export {getRooms, getLocations, addSite, renameSite, addRoom, renameRoom}
