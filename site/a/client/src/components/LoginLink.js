import React from 'react'
import { Component } from 'react'
import { Link } from 'react-router-dom'
import {
  Menu,
} from 'semantic-ui-react'

class LoginLink extends Component {
  render() {
    return (
      <Menu.Item as={ Link } name='login' to='login' active={this.props.active}>Login</Menu.Item>
    )
  }
}

export default LoginLink
