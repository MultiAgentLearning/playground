/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { Icon, Table } from 'semantic-ui-react'

class AgentTableRow extends Component {
  render() {
    return (
      <Table.Row>
        <Table.Cell>{this.name}</Table.Cell>
        <Table.Cell>{this.record}</Table.Cell>
        <Table.Cell>{this.battles}</Table.Cell>
      </Table.Row>
    )
  }
}

class AgentTable extends Component {
  render() {
    return (
      <Table celled striped>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Agents</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        
        <Table.Body>
          {this.agents.map((agent, i) => <AgentTableRow agent={agent} key={i} />)}
        </Table.Body>
      </Table>
    );
  }
}

export default AgentTable
