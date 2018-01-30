import { handleResponse } from '../utils'

export const dataService = {
  getBattles,
  getAgents,
}

export function getBattles(slug) {
  const requestOptions = {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  };
  
  return fetch('/api/get_battles/' + slug, requestOptions).then(handleResponse);
}

export function getAgents(slug) {
  const requestOptions = {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  };
  
  return fetch('/api/get_agents/' + slug, requestOptions).then(handleResponse);
}

