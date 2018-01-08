import { agentConstants } from '../constants';

export function battles(state = {}, action) {
  switch (action.type) {
    case agentConstants.GET_BATTLES_REQUEST:
      return {};
    case agentConstants.GET_BATTLES_SUCCESS:
      return {
        battles: action.battles,
      };
    case agentConstants.GET_BATTLES_FAILURE:
      return {};
    default:
      return state
  }
}

export function agents(state = {}, action) {
  switch (action.type) {
    case agentConstants.GET_AGENTS_REQUEST:
      return {};
    case agentConstants.GET_AGENTS_SUCCESS:
      return {
        agents: action.agents
      };
    case agentConstants.GET_AGENTS_FAILURE:
      return {};
    default:
      return state
  }
}
