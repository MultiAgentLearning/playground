import React from 'react'
import { Component } from 'react'
import {
  Button,
  Menu,
} from 'semantic-ui-react'

class DiscordLink extends Component {
  render() {
    return (
      <Menu.Item as='a' href='https://discord.gg/wjVJEDc' target='_blank' className='item'>
      <Button>Discord</Button>
      </Menu.Item>
    );
  }
}

export default DiscordLink
