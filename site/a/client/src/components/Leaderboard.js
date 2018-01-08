/** jsx React.DOM */
import React from 'react';
import { Component } from 'react'
import {
  Container,
  Header,
  Image,
  Menu,
  Table,
} from 'semantic-ui-react'

class Leaderboard extends Component {
  state = {
    leaderboard: 'ffa'
  }

  ffa() {
    this.setState({leaderboard: 'ffa'})
  }

  teamShare() {
    this.setState({leaderboard: 'teamShare'})
  }

  teamNoShare() {
    this.setState({leaderboard: 'teamNoShare'})
  }

  teamComm() {
    this.setState({leaderboard: 'teamComm'})
  }

  render() {
    return (
      <div>
        <Menu size='small' tabular >
          <Container>
            <Menu.Item as="a" onClick={(e) => this.ffa(e)} active={this.state.leaderboard === 'ffa'}>FFA</Menu.Item>
            <Menu.Item as="a" onClick={(e) => this.teamShare(e)} active={this.state.leaderboard === 'teamShare'}>2v2</Menu.Item>
            <Menu.Item as="a" onClick={(e) => this.teamNoShare(e)} active={this.state.leaderboard === 'teamNoShare'}>2v2 Hard</Menu.Item>
            <Menu.Item as="a" onClick={(e) => this.teamComm(e)} active={this.state.leaderboard === 'teamComm'}>2v2 Radio</Menu.Item>
          </Container>
        </Menu>
        
        <Table basic='very' celled collapsing>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Rank</Table.HeaderCell>
              <Table.HeaderCell>Creator</Table.HeaderCell>
              <Table.HeaderCell>Agent</Table.HeaderCell>
              <Table.HeaderCell>Record</Table.HeaderCell>
              <Table.HeaderCell>Games</Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            <Table.Row>
              <Table.Cell>
                1
              </Table.Cell>
              <Table.Cell>
                <Header as='h4' image>
                  <Image src={process.env.PUBLIC_URL + '/images/avatar/small/matthew.png'} rounded size='mini' />
                  <Header.Content>
                    Hardmaru
                  </Header.Content>
                </Header>
              </Table.Cell>
              <Table.Cell>
                TheEvolvers
              </Table.Cell>
              <Table.Cell>
                7-1
              </Table.Cell>
              <Table.Cell>
                vsBritzPPO, vsShallowHeart, ...
              </Table.Cell>
            </Table.Row>
            <Table.Row>
              <Table.Cell>
                2
              </Table.Cell>
              <Table.Cell>
                <Header as='h4' image>
                  <Image src={process.env.PUBLIC_URL + '/images/avatar/small/mark.png'} rounded size='mini' />
                  <Header.Content>
                    DennyBritz
                  </Header.Content>
                </Header>
              </Table.Cell>
              <Table.Cell>
                BritzPPO
              </Table.Cell>
              <Table.Cell>
                5-2
              </Table.Cell>
              <Table.Cell>
                vsTheEvolvers, vsSmeagol, ...
              </Table.Cell>
            </Table.Row>
            <Table.Row>
              <Table.Cell>
                3
              </Table.Cell>
              <Table.Cell>
                <Header as='h4' image>
                  <Image src={process.env.PUBLIC_URL + '/images/avatar/small/matthew.png'} rounded size='mini' />
                  <Header.Content>
                    Hardmaru
                  </Header.Content>
                </Header>
              </Table.Cell>
              <Table.Cell>
                NextGen
              </Table.Cell>
              <Table.Cell>
                5-3
              </Table.Cell>
              <Table.Cell>
                vsFalafelSandwich, vsSmeagol, ...
              </Table.Cell>
            </Table.Row>
          </Table.Body>
        </Table>
      </div>
    );
  }
}

export default Leaderboard
