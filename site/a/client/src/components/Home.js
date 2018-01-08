/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { connect } from 'react-redux';
import DiscordLink from './DiscordLink'
import GithubLink from './GithubLink'
import HeaderFloating from './HeaderFloating'
import HeaderStationary from './HeaderStationary'
import Leaderboard from './Leaderboard'
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

class Home extends Component {
  constructor(props) {
    super(props)
    this.state = {}
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
        { visible ? <HeaderFloating loggedIn={this.props.loggedIn} /> : null }

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
              <HeaderStationary loggedIn={this.props.loggedIn} active="home" />
            </Container>

            <Container text>
              <Header
                as='h1'
                content='POMmerman'
                style={{ fontSize: '4em', fontWeight: 'normal', marginBottom: 0, marginTop: '3em' }}
              />
              <Header
                as='h2'
                content='Train your team of AI agents. Compete against theirs.'
                style={{ fontSize: '1.7em', fontWeight: 'normal' }}
              />
              <Header
                as='h2'
                content='(Behind this, put a video of agents playing.)'
                style={{ fontSize: '1.7em', fontWeight: 'normal' }}
              />
              <Leaderboard />
            </Container>
          </Segment>
        </Visibility>

        <Segment style={{ padding: '8em 0em' }} vertical>
          <Grid container stackable verticalAlign='middle'>
            <Grid.Row>
              <Grid.Column width={8}>
                <Header as='h3' style={{ fontSize: '2em' }}>Build an AI to Compete against the World.</Header>
                <p style={{ fontSize: '1.33em' }}>
                  We are <a href="https://twitter.com/hardmaru">machine</a> <a href="https://twitter.com/dennybritz">learning</a> <a href="https://twitter.com/cinjoncin">researchers</a> building intelligent agents that can operate in environments with other agents, both cooperatively and adversarially.
                  Whether you are a student or a well-oiled machine, we want you to help us advance the state of the art by building agents.
                </p>
                <Header as='h3' style={{ fontSize: '2em' }}>TensorFlow, PyTorch, Java, Anything.</Header>
                <p style={{ fontSize: '1.33em' }}>
                  The game is Pommerman, a variant of the famous Bomberman. The difference is that each agent sees only the small part of the board in their view.
                  There are four different competitions: FFA, 2v2, 2v2 with distinct agents, and 2v2 with communication.
                </p>
                <Header as='h3' style={{ fontSize: '2em' }}>Any amount of resources. We will host it.</Header>
                <p style={{ fontSize: '1.33em' }}>
                  When you enter an agent, we will run it against a gamut of other players' agents. Glory awaits in the post-match replay, the Discord, and of course the leaderboard.
                </p>
              </Grid.Column>
              <Grid.Column floated='right' width={6}>
                <Image
                  bordered
                  rounded
                  size='large'
                  src={process.env.PUBLIC_URL + '/images/wireframe/white-image.png'}
                />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
              <Grid.Column textAlign='center'>
                <Button size='huge'>Watch a quick game.</Button>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Segment>

        <Segment style={{ padding: '8em 0em' }} vertical>
          <Container text>
            <Header as='h3' style={{ fontSize: '2em' }}>How to get started.</Header>
            <p style={{ fontSize: '1.33em' }}>
              Signup and join our Discord. Then check out the Github, which has all the instructions and details for training an agent in the environment. You can have one competing in 10 minutes (we timed it).
            </p>
            <GithubLink />
            <DiscordLink />

            <Divider
              as='h4'
              className='header'
              horizontal
              style={{ margin: '3em 0em', textTransform: 'uppercase' }}
            >
            </Divider>

            <Header as='h3' style={{ fontSize: '2em' }}>Why?</Header>
            <p style={{ fontSize: '1.33em' }}>
              The best way to push the research community forward is through strong benchmarks that test different facets of intelligence and around which people can rally. While there are suitable efforts in other areas of Machine Learning, such as <a href="https://github.com/mgbellemare/Arcade-Learning-Environment">Atari</a> and <a href="http://www.image-net.org/">ImageNet</a>, the multi-agent field is lacking and we want to rectify that.
            </p>
          </Container>
        </Segment>
        
        <Segment inverted vertical style={{ padding: '2em 0em' }}>
          <Container>
          </Container>
        </Segment>
      </div>
    )
  }
}

function mapStateToProps(state) {
  const { loggedIn, user } = state.authentication;
  return {
    loggedIn,
    user
  };
}

const connectedHome = connect(mapStateToProps)(Home);
export { connectedHome as Home };
