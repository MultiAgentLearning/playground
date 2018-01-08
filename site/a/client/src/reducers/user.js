import { userConstants } from '../constants';

let token = JSON.parse(localStorage.getItem('token'));
const initialState = token ? { loggedIn: true, token } : {};

export function authentication(state = initialState, action) {
  switch (action.type) {
    case userConstants.LOGIN_REQUEST:
      return {
        loggingIn: true,
        user: action.user
      };
    case userConstants.LOGIN_SUCCESS:
      return {
        loggedIn: true,
        user: action.user
      };
    case userConstants.LOGIN_FAILURE:
      return {};
    case userConstants.LOGOUT:
      return {
        loggedIn: false,
        user: null
      };
    case userConstants.GET_LOGGEDIN_USER_REQUEST:
      return {
        checkingToken: true,
        token: action.token
      };
    case userConstants.GET_LOGGEDIN_USER_SUCCESS:
      return {
        loggedIn: true,
        user: action.user
      };
    case userConstants.GET_LOGGEDIN_USER_FAILURE:
      return {};
    default:
      return state
  }
}

export function registration(state = {}, action) {
  switch (action.type) {
    case userConstants.REGISTER_REQUEST:
      return { registering: true, email: action.email };
    case userConstants.REGISTER_SUCCESS:
      return { registering: false, registered: true, user: action.user };
    case userConstants.REGISTER_FAILURE:
      return { registering: false, registered: false, error: action.error };
    default:
      return state
  }
}
