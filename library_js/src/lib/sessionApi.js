const request = require('superagent');

const validateSession = function(signum, secret) {
  return new Promise((resolve, reject) => {
    request
      .post(`${window.__appUrl}/api/login/validate`)
      .send({signum: signum, secret: secret})
      .type('application/json')
      .end((err, res) => {
        if(err) {
          reject();
        } else {
          resolve();
        }
      });
  });
}

const deleteSessionApi = function(signum, secret) {
  return new Promise((resolve, reject) => {
    let url = `${window.__appUrl}/api/login/delete`;
    request
      .post(url)
      .send({
        signum: signum,
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
const createSession = function(signum, password) {
  console.log("createSession");
  return new Promise((resolve, reject) => {
    let url = `${window.__appUrl}/api/login`;
    request
    .post(url)
    .send({
      signum: signum,
      password: password
    })
    .type('application/json')
    .on('error', (err) => {
      console.log(err);
      reject(err);
    })
    .end((err, res) => {
      resolve({
        signum: signum,
        secret: res.body.secret
      });
    });
  });
}

export {validateSession, deleteSessionApi, createSession};
