/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { connect } from 'react-redux';
import { history } from '../utils';
import { agentActions } from '../actions';
import HeaderFloating from './HeaderFloating'
import HeaderStationary from './HeaderStationary'
import AgentTable from './AgentTable'
import BattleTable from './BattleTable'
import {
  Button,
  Container,
  Divider,
  Grid,
  Header,
  Image,
  Segment,
  Visibility,
} from 'semantic-ui-react'

class Profile extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loaded: false
    }
  }

  componentDidMount() {
    let params = this.props.match.params;
    console.log('CDM')
    console.log(params);
    console.log(this.props);
    if (params) {
      this.getBattles(params.name)
      this.getAgents(params.name)
    } else {
      this.getBattles(this.props.user.slug)
      this.getAgents(this.props.user.slug)
    }
  }

  componentWillReceiveProps(props) {
    let params = props.match.params;
    console.log('CWRP');
    console.log(params);
    console.log(this.props);
    if (params && params.name === props.user.slug) {
      history.push('/me')
    }
  }

  getBattles() {
    this.props.dispatch(agentActions.getBattles());
  }

  getAgents() {
    this.props.dispatch(agentActions.getAgents());
  }

  hideHeader = () => this.setState({
    visible: false
  })
  showHeader = () => this.setState({
    visible: true
  })

  render() {
    const { visible } = this.state

    return (
      <div>
        { visible ? <HeaderFloating loggedIn={true} /> : null }

        <Visibility
          onBottomPassed={this.showHeader}
          onBottomVisible={this.hideHeader}
          once={false}
        >
          <Segment
            textAlign='center'
            style={{ minHeight: 700, padding: '1em 0em' }}
            vertical
          >
            <Container>
              <HeaderStationary loggedIn={true} active="profile" />
            </Container>

            <Container text style={{ marginTop: '7em' }}>
              <Header as='h1'>{this.props.user.name}</Header>
              <AgentTable agents={this.props.agents} />
              <BattleTable battles={this.props.battles} />
            </Container>
          </Segment>
        </Visibility>
      </div>
    )
  }
}

function mapStateToProps(state) {
  const { loggedIn, user } = state.authentication;
  const { agents, battles } = state.data;
  return {
    loggedIn,
    user,
    agents,
    battles
  };
}

const connectedProfile = connect(mapStateToProps)(Profile);
export { connectedProfile as Profile };
