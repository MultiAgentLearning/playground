/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { userActions } from '../actions';
import { connect } from 'react-redux';
import {
  Button,
  Menu,
} from 'semantic-ui-react'

class SubmitAgentButton extends Component {
  constructor(props) {
    super(props);
    this.openSubmitModal = this.openSubmitModal.bind(this);
  }

  openSubmitModal() {
    /* this.props.dispatch(userActions.logout());*/
  }

  render() {
    return (
      <Menu.Item as='a' onClick={this.openSubmitModal} className='item'>
      <Button>Submit Agent</Button>
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

const connectedSubmitAgentButton = connect(mapStateToProps)(SubmitAgentButton);
export { connectedSubmitAgentButton as SubmitAgentButton };
