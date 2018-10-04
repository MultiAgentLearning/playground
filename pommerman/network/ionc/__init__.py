#!/usr/bin/env python
# IonClient Main

# Global Imports
import ui
from . import constants as c
from .network import network as net
from signal import signal, SIGINT
from gym.spaces import Discrete

# Global Variables
l=c.lang_en

# Functions
def init():
    # Section I - Prompts
    global n # We want the network variable to be a global
    def exit_handler(_s,_h):
        ui.info(ui.yellow, "Exiting..") # Inform the user about exiting
        exit(0) # Exit..
    signal(SIGINT, exit_handler) # Setup the exit handler
    if ui.ask_yes_no(l.server_prompt.value): # Check if user wants to connect to a custom server or not
        ip=ui.ask_string(l.server_ip.value) # If yes, prompt for IP of server
    else:
        ip="play.pommerman.com:5050" # If no, then set IP to that of the default server
    ui.info(l.server_connecting_p1.value, ui.yellow, l.server_connecting_p2.value, ui.reset, l.server_connecting_p3.value) # Write out connecting statement
    if(ip==None): # Check if IP isn't None
        ui.fatal(l.e_invalid_ip.value) # Write the error to the terminal
    n=net(ip) # Try connecting to the server
    z=n.check() # Try checking the server status
    if not z[0]: # If connection was unsuccessful
        ui.fatal(l[z[1]].value) # Write the reason to terminal
    else: # If the connection was successful
        ui.info(l.server_connected.value, ui.yellow, l.server_players.value, str(z[1])+",", l.server_matches.value, z[2]) # Print out success message
    intent() # Get the intent of the user
    # End of Section I

def intent():
    # Section II - Get Intent of User
    i=ui.ask_choice(l.intent.value,[l.intent_match.value, l.intent_room.value, l.intent_replay.value, l.intent_exit.value]) # Get intent of user via user interface
    if i == l.intent_match.value:
        match() # Call match() function
    elif i == l.intent_room.value:
        match(True) # Call match() function with True
    elif i == l.intent_replay.value:
        replay() # Call replay() function
    elif i == l.intent_exit.value:
        exit(0) # Exit the application
    # End of Section II

def match(room=False):
    # Local Imports
    from os import getcwd
    from sys import path
    from importlib import import_module
    # Section IIIA - Match
    if room: # If room is True
        room=str(ui.ask_string(l.room_code.value)) # Ask for room name
    path.append(getcwd()) # Add Current Working Directory to import path otherwise we won't be able to import modules from here
    a=import_module(ui.ask_string(l.match_import.value)) # Prompt user and import agent module
    z=ui.ask_string(l.match_class_name.value) # Prompt user for agent class
    if not z in a.__dir__(): # If class isn't in module
        ui.fatal("Cannot find class in module file") # Write error to terminal
    a=getattr(a,z) # Scope to agent class as we don't need anything else from the module
    if(getattr(a,"act")): # Check if the agent has an `act` function
        ui.info(ui.green, l.match_agent_success.value) # If yes, then notify the user
    a=a() # Initiate the agent class
    ui.info(ui.yellow, l.server_comm.value) # Inform user about server communication
    n.join_list(room) # Get into the match waiting list
    ui.info(l.match_variant.value, ui.yellow, n.mode) # Write the server mode to the terminal
    ui.info(ui.yellow, l.match_wait.value) # Inform user about waiting for match
    n.waitm() # Wait for match to start
    ui.info(l.match_run.value, "#"+n.m_id) # Inform user that the match has started and give them the match ID
    while(True): # Run while we don't receive a match end request or an error
        m=n.match_get() # Get the obs and step ID from the server
        if(m[0]!=False): # If the function hasn't errored out
            q=a.act(m[0], Discrete(6)) # Store the result of the agent's action
            e=n.send_move(q, m[1]) # Try and send the action
            if(e[0]==False): # If sending the move failed
                ui.fatal(l[e[1]].value) # Write the error message to the terminal
        elif(m[0]==False and isinstance(m[1], int)): # If the match has ended
            a.episode_end(m[1]) # Call the episode end for the agent
            if(m[1]==1): # If the reward is 1
                ui.info(l.match_won.value) # Write out win to terminal
            if(m[1]==-1): # If the reward is -1
                ui.info(l.match_loss_draw.value) # Write out loss/draw to terminal
            break # Break out of the while loop
        else: # If an error has occured
            ui.info(ui.yellow, l[m[1]].value) # Warn the users about the error
    ui.info(l.match_replay.value, ui.yellow, n.m_id) # Inform the user about replaying the match
    if ui.ask_yes_no(l.match_ask_replay.value): # Ask if the user wants to replay the match right now
        replay(n.m_id) # Replay the match
    else: # Else..
        intent() # Go back to the intent prompt
    # End of Section IIIA

def replay(id=False):
    # Section IIIB - Replay
    if not id: # If ID isn't specified
        id=str(ui.ask_string(l.replay_prompt.value)) # Prompt user for match ID (For replaying)
        if id==None: # If the match ID is invalid
            ui.fatal(l.e_invalid_id.value) # Write it out to terminal
    ui.info(l.server_replay_p1.value, ui.yellow, "#"+str(id), ui.reset, l.server_replay_p2.value) # Notify user about server communication
    r=n.get_replay(id) # Try retrieving replay from server
    if not r[0]: # If match couldn't be retrieved
        ui.fatal(l[r[1]].value) # Write the reason to terminal
    ui.info(l.replay_start.value, ui.yellow, "#"+str(id)) # Print out success message
    r=r[1] # Scope to replay data
    # Replay the file
    # Local Imports
    from pommerman import make
    from pommerman.agents import BaseAgent
    from time import sleep
    from numpy import array
    env=make(r["mode"], [BaseAgent(), BaseAgent(), BaseAgent(), BaseAgent()]) # Create an pommerman env.
    env.reset() # Reset the environment
    env._board=array(r["board"]) # Set the state to that of the recorded game
    env._render_fps=30 # Change the render FPS to 30 so the game looks smoother
    for i in r["actions"]: # Iterate over the actions
        env.render() # Render the environment
        rew=env.step(i)[1] # Take the action
    sleep(0.5) # Sleep for a bit after the last action so the user can see it
    if(rew!=r["reward"]): # If the reward doesn't match
        ui.info(ui.yellow, l.replay_nomatch.value) # Inform the user about the mismatch
    env.close() # Close the environment
    ui.info(ui.yellow, l.replay_end.value) # Inform the user about the replay ending
    intent() # Go back to the intent prompt
    # End of Section IIIB

if __name__=="__main__":
    init()