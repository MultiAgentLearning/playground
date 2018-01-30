import React from 'react';
import { Route, Redirect } from 'react-router-dom';

/* export function AuthenticatedRoute(Component) {
 * 
 *   class Authenticated extends React.Component {
 *     constructor(props) {
 *       super(props);
 *       this.satte = { loaded: false };
 *     }
 * 
 *     componentWillMount() {
 *       this.checkAuthenticated();
 *     }
 * 
 *     checkAuthenticated() {
 *       
 *     }*/

export const AuthenticatedRoute = ({ component: Component, ...rest }) => (
  <Route {...rest} render={props => (
    localStorage.getItem('token')
    ? <Component authenticated={true} {...props} />
                             : <Redirect to={{ pathname: '/login', state: { from: props.location } }} />
  )} />
)
