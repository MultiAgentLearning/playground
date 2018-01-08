/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import {
  Menu,
} from 'semantic-ui-react'
import DiscordLink from './DiscordLink'
import GithubLink from './GithubLink'
import LoginLink from './LoginLink'
import ProfileLink from './ProfileLink'
import SignupLink from './SignupLink'

class HomeMenuStationary extends Component {
  state = {
    loggedIn: false,
    user: null
  };

  renderLoggedIn() {
    return (
      <Menu pointing secondary size='large'>
        <Menu.Item as='a' active>Pommerman</Menu.Item>
        <ProfileLink />
        <Menu.Menu position='right'>
          <GithubLink />
          <DiscordLink />
        </Menu.Menu>
      </Menu>
    );
  }

  renderLoggedOut() {
    return (
      <Menu pointing secondary size='large'>
        <Menu.Item as='a' active>Pommerman</Menu.Item>
        <LoginLink />
        <SignupLink />
        <Menu.Menu position='right'>
          <GithubLink />
          <DiscordLink />
        </Menu.Menu>
      </Menu>
    );
  }
  
  render() {
    if (this.state.loggedIn) {
      return this.renderLoggedIn();
    } else {
      return this.renderLoggedOut();
    }
  }
}

export default HomeMenuStationary
