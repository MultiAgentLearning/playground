/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { connect } from 'react-redux';
import { history } from '../utils';
import { dataActions } from '../actions';
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
      this.getData(params.name);
    } else if (this.props.user) {
      this.getData(this.props.user.slug);
    }
  }

  componentWillReceiveProps(props) {
    let params = props.match.params;
    console.log('CWRP');
    console.log(params);
    console.log(props);
    if (params && props.user && params.name === props.user.slug) {
      history.push('/me')
    } 
  }

  getData(slug) {
    this.getBattles(slug)
    this.getAgents(slug)

  }
  getBattles(slug) {
    this.props.dispatch(dataActions.getBattles(slug));
  }

  getAgents(slug) {
    this.props.dispatch(dataActions.getAgents(slug));
  }

  hideHeader = () => this.setState({
    visible: false
  })
  showHeader = () => this.setState({
    visible: true
  })

  render() {
    const { visible } = this.state

    var name = ''
    var agents = [];
    var battles = [];

    if (this.props.user) {
      name = this.props.user.name;
    }
    if (this.props.agents) {
      agents = this.props.agents;
    }
    if (this.props.battles) {
      battles = this.props.battles;
    }

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
              <Header as='h1'>{name}</Header>
              <AgentTable agents={agents} />
              <BattleTable battles={battles} />
            </Container>
          </Segment>
        </Visibility>
      </div>
    )
  }
}

function mapStateToProps(state) {
  console.log(state);
  const { loggedIn, user } = state.authentication;
  const { agents , battles } = state;
  return {
    loggedIn,
    user,
    agents,
    battles
  };
}

const connectedProfile = connect(mapStateToProps)(Profile);
export { connectedProfile as Profile };
