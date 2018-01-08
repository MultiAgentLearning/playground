/** jsx React.DOM */
import React from 'react'
import { Component } from 'react'
import { Icon, Table } from 'semantic-ui-react'

class BattleTableRow extends Component {
  render() {
    return (
      <Table.Row>
        <Table.Cell>{this.date}</Table.Cell>
        <Table.Cell>{this.agents}</Table.Cell>
        <Table.Cell>{this.players}</Table.Cell>
        <Table.Cell>{this.resultp}</Table.Cell>
      </Table.Row>
    )
  }
}

class BattleTable extends Component {
  render() {
    return (
      <Table celled striped>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Battles</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        
        <Table.Body>
          {this.battles.map((battle, i) => <BattleTableRow battle={battle} key={i} />)}
        </Table.Body>
      </Table>
    );
  }
}

export default BattleTable
