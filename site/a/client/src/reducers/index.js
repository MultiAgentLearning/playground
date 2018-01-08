import { combineReducers } from 'redux';

import { authentication, registration } from './user';
import { alert } from './alert';

const rootReducer = combineReducers({
  authentication,
  registration,
  alert
});

export default rootReducer;
