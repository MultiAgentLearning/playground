import React from 'react';
import { userActions } from '../actions';
import { connect } from 'react-redux';


export function WrapLoggedInCheck(Component) {

  class LoggedIn extends React.Component {
    constructor(props) {
      super(props);
      this.state = { loaded: false, gettingUserInfo: false };
    }

    componentWillMount() {
      console.log('CWM')
      this.checkLoggedIn(this.props);
    }

    componentWillReceiveProps(props) {
      console.log('CWRP in WLIC')
      this.checkLoggedIn(props);
    }

    checkLoggedIn(props) {
      console.log('CLI!');
      const { dispatch } = this.props;
      const token = JSON.parse(localStorage.getItem('token'));
      if (token && (!props.loggedIn || !props.user) && !this.state.gettingUserInfo) {
        this.setState({gettingUserInfo: true});
        dispatch(userActions.getLoggedInUser(token));
      } else {
        this.setState({
          loaded: true,
          gettingUserInfo: false
        });
      }
    }
    
    render() {
      return (
        <div>
        {this.state.loaded ? <Component {...this.props} /> : null}
        </div>
      );
    }
  }

  function mapStateToProps(state) {
    const { loggedIn, user } = state.authentication;
    return {
      loggedIn,
      user,
    };
  }

  return connect(mapStateToProps)(LoggedIn);
}

