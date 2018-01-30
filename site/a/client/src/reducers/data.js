import { dataConstants } from '../constants';

export function battles(state = [], action) {
  switch (action.type) {
    case dataConstants.GET_BATTLES_REQUEST:
      return [];
    case dataConstants.GET_BATTLES_SUCCESS:
      return action.battles;
    case dataConstants.GET_BATTLES_FAILURE:
      return [];
    default:
      return state
  }
}

export function agents(state = [], action) {
  switch (action.type) {
    case dataConstants.GET_AGENTS_REQUEST:
      return [];
    case dataConstants.GET_AGENTS_SUCCESS:
      return action.agents;
    case dataConstants.GET_AGENTS_FAILURE:
      return [];
    default:
      return state
  }
}
