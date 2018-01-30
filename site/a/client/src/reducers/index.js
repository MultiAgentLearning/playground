import { combineReducers } from 'redux';

import { authentication, registration } from './user';
import { agents, battles } from './data';
import { alert } from './alert';

const rootReducer = combineReducers({
  agents,
  authentication,
  battles,
  registration,
  alert
});

export default rootReducer;
