const request = require('superagent');

const validateSession = function(session_id, secret) {
  return new Promise((resolve, reject) => {
    request
      .post(`${window.API_URL}/api/login/validate`)
      .send({session_id: session_id, secret: secret})
      .type('application/json')
      .end((err, res) => {
        if(err) {
            console.log(err, res)
          reject();
        } else {
          resolve();
        }
      });
  });
}

const deleteSessionApi = function(session_id, secret) {
  return new Promise((resolve, reject) => {
    let url = `${window.API_URL}/api/login/delete`;
    request
      .post(url)
      .send({
        session_id: session_id,
        secret: secret
      })
      .type('application/json')
      .end((err, res) => {
        if (err) {
          reject();
        }
        resolve();
      });
  });
}
const createSession = function(user, password) {
  return new Promise((resolve, reject) => {
    let url = `${window.API_URL}/api/login`;
    request
    .post(url)
    .send({
      user: user,
      password: password
    })
    .type('application/json')
    .on('error', (err) => {
      console.log(err);
      reject(err);
    })
    .end((err, res) => {
      resolve({
        session_id: res.body.session_id,
        secret: res.body.session_secret
      });
    });
  });
}

export {validateSession, deleteSessionApi, createSession};
