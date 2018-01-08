import React from 'react';
import { userActions } from '../actions';

export function DetermineLoggedIn(Component) {

  class LoggedIn extends React.Component {
    componentWillMount() {
      this.checkLoggedIn();
      this.state = {
        loaded_if_needed: false,
      };
    }

    componentWillReceiveProps(props) {
      if (!props.loggedIn || !props.user) {
        const token = localStorage.getItem('token');
        console.log(token);
        if (token) {
          dispatch(userActions.getLoggedInUser(token));
        } 
      } else {
        this.setState({
          loaded_if_needed: true,
        });
      }
    }

    render() {
      return (
        <div>
        {this.state.loaded_if_needed ? <Component {...this.props} /> : null}
        </div>
      );
    }
  }

  return AuthenticatedComponent;
}

function mapStateToProps(state) {
  const { loggedIn, user } = state.authentication;
  return {
    loggedIn,
    user,
  };
}

const connectedLoggedIn = connect(mapStateToProps)(LoggedIn);
export { connectedLoggedIn as LoggedIn };
