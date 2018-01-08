import { handleResponse, authHeader } from '../utils'

export const userService = {
  login,
  logout,
  register,
  getLoggedInUser,
};

function login(email, password) {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  };
  
  return fetch('/api/get_token', requestOptions)
    .then(response => {
      if (response.ok) {
        return response.json().then(data => {
          localStorage.setItem('token', JSON.stringify(data.token));
          getLoggedInUser()
        });
      } else {
        return Promise.reject(response.statusText);
      }
    })
    .then(error => {
      return Promise.reject(error);
    });
}

function logout() {
  // remove user from local storage to log user out
  localStorage.removeItem('token');
}

function register(name, email, password) {
  var user = {name: name, email: email, password: password}
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  };
  
  return fetch('/api/create_user', requestOptions).then(handleResponse);
}

function getLoggedInUser() {
  const requestOptions = {
    method: 'GET',
    headers: authHeader()
  };
  
  return fetch('/api/user', requestOptions).then(handleResponse);  
}


