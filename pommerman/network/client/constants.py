#!/usr/bin/env python
"""This holds all of the constants used by ion_client"""

import enum


class Strings(enum.Enum):
    """Define all the strings"""
    server_prompt = "Connect to custom server ?"
    server_ip = "Enter IP of server to connect to:"
    server_connecting_p1 = "Connecting to"
    server_connecting_p2 = "IonPlayer"
    server_connecting_p3 = "servers"
    server_connected = "Connected to server:"
    server_players = "Concurrent players:"
    server_matches = "Concurrent matches:"
    server_comm = "Communicating with server ✈"
    server_replay_p1 = "Retrieving match"
    server_replay_p2 = "from server"
    intent = "What do you want to do ?"
    intent_match = "Join the public room"
    intent_room = "Join a room"
    intent_replay = "Look at a replay"
    intent_exit = "Quit the application"
    room_code = "Enter the name of the room you want to join/create"
    match_import = "Input the module which has your agent's class. EG: pommerman.agents"
    match_class_name = "Input the name of your agent's class (So class.act() is valid). EG: SimpleAgent"
    match_agent_success = "The agent was successfully imported"
    match_variant = "The variant of Pommerman used:"
    match_wait = "Waiting for Server to allocate players to match.."
    match_run = "Running match.."
    match_won = "Your agent has won!"
    match_loss_draw = "Your agent has either lost or there was a draw"
    match_replay = "You can now view the replay using the match ID:"
    match_ask_replay = "Do you want to replay the current match ?"
    match_agent = "Your agent was"
    replay_prompt = "Input the ID of the match ?"
    replay_start = "Replaying match.."
    replay_nomatch = "The reward of the replay doesn't match that of the game ?"
    replay_end = "The replay is over."
    error_no_recv = "The observation wasn't successfully retrieved from the server"


class NetworkCommands(enum.Enum):
    """Define all the network commands"""
    check = 0
    ping = 1
    match = 2
    room = 3
    match_start = 4
    match_act = 5
    match_end = 6
    replay = 7
    status_ok = 10
    status_fail = 11
    status_full = 12
    status_reg = 13


class Exceptions(enum.Enum):
    """Define all the exceptions"""
    net_connect_fail = "Couldn't connect to the server"
    net_respond_fail = "The server didn't respond correctly"
    net_invalid_response = "The server sent an invalid response"
    net_server_full = "The server is full"
    net_server_closed = "The connection to the server was closed"
    match_full = "The maximum amount of concurrent matches on the has been exceeded"
    room_full = "The room is full"
    replay_notfound = "Couldn't find replay on server"
    replay_no_reward = "The current reward doesn't match the expected reward"
    invalid_ip = "The provided IP is invalid"
    invalid_id = "The provided match ID is invalid"
    invalid_room = "The provided room name is invalid"
    invalid_class = "Cannot find class in module file"
