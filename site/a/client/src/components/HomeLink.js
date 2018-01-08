import React from 'react'
import { Component } from 'react'
import { Link } from 'react-router-dom'
import {
  Menu,
} from 'semantic-ui-react'

class HomeLink extends Component {
  render() {
    return (
      <Menu.Item as={ Link } name='home' to='/' active={this.props.active}>Pommerman</Menu.Item>
    )
  }
}

export default HomeLink
