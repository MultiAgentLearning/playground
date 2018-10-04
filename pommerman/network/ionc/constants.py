#!/usr/bin/env python
# IonClient Constants

# Imports
from enum import Enum

# String Definitions
class lang_en(Enum):
    server_prompt="Connect to custom server ?"
    server_ip="Enter IP of server to connect to:"
    server_connecting_p1="Connecting to"
    server_connecting_p2="IonPlayer"
    server_connecting_p3="servers"
    server_connected="Connected to server:"
    server_players="Concurrent players:"
    server_matches="Concurrent matches:"
    server_comm="Communicating with server ✈"
    server_replay_p1="Retrieving match"
    server_replay_p2="from server"
    intent="What do you want to do ?"
    intent_match="Look for a match"
    intent_room="Join a room"
    intent_replay="Look at a replay"
    intent_exit="Quit the application"
    room_code="Enter the name of the room you want to join/create"
    match_import="Input the folder/file which has your agent's class"
    match_class_name="Input the name of your agent class (So class.act() is valid)"
    match_agent_success="The agent was successfully imported"
    match_variant="The variant of Pommerman used:"
    match_wait="Waiting for Server to allocate players to match.."
    match_run="Running match.."
    match_won="Your agent has won!"
    match_loss_draw="Your agent has either lost or there was a draw"
    match_replay="You can now view the replay using the match ID:"
    match_ask_replay="Do you want to replay the current match ?"
    replay_prompt="Input the ID of the match ?"
    replay_start="Replaying match.."
    replay_nomatch="The reward of the replay doesn't match that of the game ?"
    replay_end="The replay is over."
    w_no_recv="The observation wasn't successfully retrieved from the server"
    e_invalid_ip="The provided IP is invalid"
    e_invalid_id="The provided match ID is invalid"
    e_invalid_room="The provided room name is invalid"
    e_connect_fail="Couldn't connect to the server"
    e_respond_fail="The server didn't respond"
    e_server_closed="The connection to the server was closed"
    e_replay_notfound="Couldn't find replay on server"

# Network-intent command definitions
class nic(Enum):
    check=0
    ping=1
    match=2
    room=3
    match_start=4
    match_act=5
    match_end=6
    replay=7
    s_ok=10
    s_fail=11
    s_full=12
    s_reg=13