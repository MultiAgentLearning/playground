import React from 'react'
import { Component } from 'react'
import { Link } from 'react-router-dom'
import {
  Menu,
} from 'semantic-ui-react'

class ProfileLink extends Component {
  render() {
    return (
      <Menu.Item as={ Link } name='profile' to='me' active={this.props.active}>Profile</Menu.Item>
    )
  }
}

export default ProfileLink
