/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { userActions } from '../actions';
import { connect } from 'react-redux';
import {
  Button,
  Menu,
} from 'semantic-ui-react'

class LogoutButton extends Component {
  constructor(props) {
    super(props);
    this.logoutUser = this.logoutUser.bind(this);
  }

  logoutUser() {
    this.props.dispatch(userActions.logout());
  }

  render() {
    return (
      <Menu.Item as='a' onClick={this.logoutUser} className='item'>
        <Button>Logout</Button>
      </Menu.Item>
    )
  }
}

function mapStateToProps(state) {
  const { loggingIn } = state.authentication;
  return {
    loggingIn
  };
}

const connectedLogoutButton = connect(mapStateToProps)(LogoutButton);
export { connectedLogoutButton as LogoutButton };
