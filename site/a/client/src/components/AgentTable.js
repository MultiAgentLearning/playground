/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { Icon, Table } from 'semantic-ui-react'

class AgentTableRow extends Component {
  render() {
    return (
      <Table.Row>
        <Table.Cell>{this.props.agent.name}</Table.Cell>
        <Table.Cell>{this.props.agent.record}</Table.Cell>
        <Table.Cell>{this.props.agent.battles}</Table.Cell>
      </Table.Row>
    )
  }
}

class AgentTable extends Component {
  render() {
    console.log('watat');
    console.log(this.props);
    console.log(this.props.agents);
    return (
      <Table celled striped>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Agents</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        
        <Table.Body>
          {this.props.agents.map((agent, i) => <AgentTableRow agent={agent} key={i} />)}
        </Table.Body>
      </Table>
    );
  }
}

export default AgentTable
