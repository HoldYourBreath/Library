const request = require('superagent');


const renameSite = function(siteId, newName) {
  return new Promise((resolve, reject) => {
    request
      .put(`${window.API_URL}/api/sites/${siteId}`)
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
      .get(`${window.API_URL}/api/rooms`)
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
      .get(`${window.API_URL}/api/sites`)
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
      .post(`${window.API_URL}/api/sites`)
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
	  .post(`${window.API_URL}/api/sites/${siteId}/rooms`)
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

const removeRoom = (siteId, roomId) => {
  return new Promise((resolve, reject) => {
    request
	  .delete(`${window.API_URL}/api/sites/${siteId}/rooms/${roomId}`)
	  .type('application/json')
	  .end((err, res) => {
		  if (err) {
			  reject(res.body);
		  } else {
			  resolve(res.body);
		  }
	  });
  });
};

const renameRoom = (siteId, roomId, newName) => {
  return new Promise((resolve, reject) => {
    request
      .put(`${window.API_URL}/api/sites/${siteId}/rooms/${roomId}`)
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

export {getRooms, getLocations, addSite, renameSite, addRoom, removeRoom, renameRoom};
