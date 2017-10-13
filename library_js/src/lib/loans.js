const request = require('superagent');

const newLoan = function(userId, bookId) {
  return new Promise((resolve, reject) => {
    request
      .post(`${window.API_URL}/api/loans`)
      .send({user_id: userId, book_id: bookId})
      .end((err, res) => {
        if (err) {
          reject(res.body.msg);
        } else {
          resolve(res.body);
        }
      });
  });
};

const deleteLoan = function(bookId) {
  return new Promise((resolve, reject) => {
    request
      .delete(`${window.API_URL}/api/loans/${bookId}`)
      .end((err, res) => {
        if (err) {
          reject(res.body.msg);
        } else {
          resolve(res.body);
        }
      });
  });
};

export {newLoan, deleteLoan};
