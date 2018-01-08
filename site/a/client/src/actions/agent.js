import { agentConstants } from '../constants';
import { agentService } from '../services';
import { alertActions } from './';

export const agentActions = {
  getBattles,
  getAgents,
};

function getBattles(userSlug) {
  return dispatch => {
    dispatch(request(userSlug));

    agentService.getBattles(userSlug)
                .then(
                  response => {
                    dispatch(alertActions.success('Received Battles for ' + userSlug + '.'))
                    dispatch(success(response.battles));
                  }, 
                  error => { 
                    dispatch(alertActions.error(error));
                    dispatch(failure(error))
                  }
                );
  };
  
  function request(userSlug) { return { type: agentConstants.GET_BATTLES_REQUEST, userSlug } }
  function success(battles) { return { type: agentConstants.GET_BATTLES_SUCCESS, battles } }
  function failure(error) { return { type: agentConstants.GET_BATTLES_FAILURE, error } }
}

function getAgents(userSlug) {
  return dispatch => {
    dispatch(request());

    agentService.getAgents(userSlug)
                .then(
                  response => {
                    dispatch(alertActions.success('Received Agents for ' + userSlug + '.'))
                    dispatch(success(response.agents));
                  }, 
                  error => { 
                    dispatch(alertActions.error(error));
                    dispatch(failure(error))
                  }
                );
  };
  
  function request() { return { type: agentConstants.GET_AGENTS_REQUEST } }
  function success(agents) { return { type: agentConstants.GET_AGENTS_SUCCESS, agents } }
  function failure(error) { return { type: agentConstants.GET_AGENTS_FAILURE, error } }
}
