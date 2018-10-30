#!/usr/bin/env python
"""This holds all of the constants used by ion_server"""

import enum


class Strings(enum.Enum):
    """Define all the strings"""
    sever_starting = "Server is being initiated.."
    server_ready = "Server is ready"
    server_players = "Concurrent players"
    server_matches = "Concurrent matches"
    server_exit_prompt = "Are you sure you want to stop the server ?"
    server_exit = "The server is quitting.."
    server_port = "What port would you want the server to start on ?"
    server_maxp = "What's the maximum amount of players that can be concurrently connected to the server ?"
    server_playercount_too_low = "Input a number greater than 4"
    server_timeout = "What's the timeout for the player response (In seconds) ?"
    server_mode = "Which variant of Pommerman would you like the Server to run ?"


class SubprocessCommands(enum.Enum):
    """Define all the sub-process commands"""
    get_players = 0
    update_cc = 1
    match_next = 2
    player_drop = 3
    match_end = 4


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
