/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import {
  Menu,
} from 'semantic-ui-react'
import DiscordLink from './DiscordLink'
import GithubLink from './GithubLink'
import HomeLink from './HomeLink'
import LoginLink from './LoginLink'
import { LogoutButton } from './LogoutButton'
import ProfileLink from './ProfileLink'
import SignupLink from './SignupLink'

class HeaderStationary extends Component {
  renderLoggedIn() {
    return (
      <Menu pointing secondary size='large'>
        <HomeLink active={this.props.active === "home"} />
        <ProfileLink active={this.props.active === "profile"} />
        <Menu.Menu position='right'>
          <GithubLink />
          <DiscordLink />
          <LogoutButton />
        </Menu.Menu>
      </Menu>
    );
  }

  renderLoggedOut() {
    return (
      <Menu pointing secondary size='large'>
        <HomeLink active={this.props.active === "home"} />
        <LoginLink active={this.props.active === "login"} />
        <SignupLink active={this.props.active === "signup"} />
        <Menu.Menu position='right'>
          <GithubLink />
          <DiscordLink />
        </Menu.Menu>
      </Menu>
    );
  }
  
  render() {
    if (this.props.loggedIn) {
      return this.renderLoggedIn();
    } else {
      return this.renderLoggedOut();
    }
  }
}

export default HeaderStationary
