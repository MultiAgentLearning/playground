/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import {
  Button,
  Menu,
} from 'semantic-ui-react'

class GithubLink extends Component {
  render() {
    return (
      <Menu.Item as='a' href='https://github.com/hardmaru/playground/tree/master/games/a/pommerman' target='_blank' className='item'>
        <Button>Github</Button>
      </Menu.Item>
    );
  }
}

export default GithubLink

