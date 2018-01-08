import { userConstants } from '../constants';
import { userService } from '../services';
import { alertActions } from './';
import { history } from '../utils';

export const userActions = {
  login,
  logout,
  register,
  getLoggedInUser,
};

function login(email, password) {
  return dispatch => {
    dispatch(request({email}));

    userService.login(email, password)
               .then(
                 response => {
                   console.log('LOGIN');
                   console.log(response);
                   dispatch(success(response.user));
                   history.push('/me');
                 },
                 error => {
                   dispatch(failure(error));
                   dispatch(alertActions.error(error));
                 }
               );
  };
  
  function request(user) { return { type: userConstants.LOGIN_REQUEST, user } }
  function success(user) { return { type: userConstants.LOGIN_SUCCESS, user } }
  function failure(error) { return { type: userConstants.LOGIN_FAILURE, error } }
}

function logout() {
  userService.logout();
  history.push('/');
  return { type: userConstants.LOGOUT };
}

function register(name, email, password) {
  return dispatch => {
    dispatch(request(email));

    userService.register(name, email, password)
               .then(
                 response => {
                   console.log('REGI')
                   console.log(response.token);
                   localStorage.setItem('token', JSON.stringify(response.token));
                   dispatch(authenticate(response.user));
                   dispatch(alertActions.success('Registration successful'));
                   dispatch(success(response.user));
                   history.push('/');
                 },
                 error => {
                   dispatch(failure(error));
                   dispatch(alertActions.error(error));
                 }
               );
  };
  
  function request(email) { return { type: userConstants.REGISTER_REQUEST, email } }
  function success(user) { return { type: userConstants.REGISTER_SUCCESS, user } }
  function authenticate(user) { return { type: userConstants.LOGIN_SUCCESS, user } }
  function failure(error) { return { type: userConstants.REGISTER_FAILURE, error } }
}

function getLoggedInUser(token) {
  return dispatch => {
    if (!token) {
      token = JSON.parse(localStorage.getItem('token'));
    }

    dispatch(request(token));
    userService.getLoggedInUser(token)
               .then(
                 response => {
                   dispatch(alertActions.success('User logged in.'))
                   dispatch(success(response.user));
                   dispatch(authenticate(response.user));
                 }, 
                 error => { 
                   localStorage.removeItem('token');
                   dispatch(failure(error))
                   dispatch(alertActions.error(error));
                 }
               );
  };
  
  function request() { return { type: userConstants.GET_LOGGEDIN_USER_REQUEST, token } }
  function success(user) { return { type: userConstants.GET_LOGGEDIN_USER_SUCCESS, user } }
  function authenticate(user) { return { type: userConstants.LOGIN_SUCCESS, user } }
  function failure(error) { return { type: userConstants.GET_LOGGEDIN_USER_FAILURE, error } }
}
