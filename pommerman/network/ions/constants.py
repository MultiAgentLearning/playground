#!/usr/bin/env python
# IonClient Constants

# Imports
from enum import Enum

# String Definitions
class lang_en(Enum):
    sever_starting="Server is being initiated.."
    server_ready="Server is ready"
    server_players="Concurrent players"
    server_matches="Concurrent matches"
    server_exit_prompt="Are you sure you want to stop the server ?"
    server_exit="The server is quitting.."
    server_port="What port would you want the server to start on ?"
    server_maxp="What's the maximum amount of players that can be concurrently connected to the server ?"
    server_to="What's the timeout for the player response (In seconds) ?"
    server_mode="Which variant of Pommerman would you like the Server to run ?"

# Sub-process command definitions
class spc(Enum):
    get_players=0
    update_cc=1
    match_next=2
    player_drop=3
    match_end=4

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