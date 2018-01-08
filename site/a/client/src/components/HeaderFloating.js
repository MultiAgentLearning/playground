/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import {
  Container,
  Menu,
} from 'semantic-ui-react'
import DiscordLink from './DiscordLink'
import GithubLink from './GithubLink'
import HomeLink from './HomeLink'
import LoginLink from './LoginLink'
import { LogoutButton } from './LogoutButton'
import { SubmitAgentButton } from './SubmitAgentButton'
import ProfileLink from './ProfileLink'
import SignupLink from './SignupLink'

class HeaderFloating extends Component {
  renderLoggedIn() {
    return (
      <Menu fixed='top' size='large'>
        <Container>
          <HomeLink />
          <ProfileLink />
          <SubmitAgentButton />
          <Menu.Menu position='right'>
            <GithubLink />
            <DiscordLink />
            <LogoutButton />
          </Menu.Menu>
        </Container>
      </Menu>
    );
  }

  renderLoggedOut() {
    return (
      <Menu fixed='top' size='large'>
        <Container>
          <HomeLink />
          <LoginLink />
          <SignupLink />
          <Menu.Menu position='right'>
            <GithubLink />
            <DiscordLink />
          </Menu.Menu>
        </Container>
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

export default HeaderFloating
