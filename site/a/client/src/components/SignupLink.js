import React from 'react'
import { Component } from 'react'
import { Link } from 'react-router-dom'
import {
  Menu,
} from 'semantic-ui-react'

class SignupLink extends Component {
  render() {
    return (
      <Menu.Item as={ Link } name='signup' to='signup' active={this.props.active}>Signup</Menu.Item>
    )
  }
}

export default SignupLink
