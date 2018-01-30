import { dataConstants } from '../constants';
import { dataService } from '../services';
import { alertActions } from './';

export const dataActions = {
  getBattles,
  getAgents,
};

function getBattles(userSlug) {
  return dispatch => {
    dispatch(request(userSlug));

    dataService.getBattles(userSlug)
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
  
  function request(userSlug) { return { type: dataConstants.GET_BATTLES_REQUEST, userSlug } }
  function success(battles) { return { type: dataConstants.GET_BATTLES_SUCCESS, battles } }
  function failure(error) { return { type: dataConstants.GET_BATTLES_FAILURE, error } }
}

function getAgents(userSlug) {
  return dispatch => {
    dispatch(request());

    dataService.getAgents(userSlug)
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
  
  function request() { return { type: dataConstants.GET_AGENTS_REQUEST } }
  function success(agents) { return { type: dataConstants.GET_AGENTS_SUCCESS, agents } }
  function failure(error) { return { type: dataConstants.GET_AGENTS_FAILURE, error } }
}
