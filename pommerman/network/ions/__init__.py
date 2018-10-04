#!/usr/bin/env python
# IonClient Main

# Global Imports
import ui
from multiprocessing import Process, freeze_support, Queue, Pipe
from . import constants as c
from .network import thread as net_proc
from .match import thread as match_proc
from time import sleep
from random import sample
from signal import signal, SIGINT
from pommerman import configs

# Global Variables
l=c.lang_en
spc=c.spc
msp=[] # Hold the match sub-processes

# Functions
def init():
    # Section I - Startup
    ui.info(ui.yellow, l.sever_starting.value) # Notify the user about the server starting
    port = int(ui.ask_string(l.server_port.value)) # Prompt the user for the port of the server
    max_p = int(ui.ask_string(l.server_maxp.value)) # Prompt the user for the max amount of players
    if(max_p<4):
        ui.fatal(ui.yellow, "Input a number greater than 4")
    max_m=int(max_p/4) # Max amount of matches
    timeout = float(ui.ask_string(l.server_to.value)) # Prompt the user for the timeout
    modes=[] # This holds the list of game modes
    for i in configs.__dir__(): # Iterate through functions in configs
        if(i[-4:]=="_env"): # If the function ends with environment
            id=getattr(configs, i)()["env_id"] # Set the env_id as a variable
            if(id[-2:]!="v2"): # If environment isn't a v2 one
                modes.append(id) # Add the id to the modes list
    mode = str(ui.ask_choice(l.server_mode.value, modes)) # Prompt the user for the max amount of players
    netp, rnetp = Pipe() # Network Pipe for main process communication
    qsp_net = Queue() # Network Queue for sub-process communication
    sp_net = Process(target=net_proc, args=(rnetp, qsp_net, port, max_p, int(max_p/4), mode, timeout)) # Define the network manager sub-process
    sp_net.start() # Start the network manager sub-process
    ui.info(ui.yellow, l.server_ready.value, ui.white, ui.Symbol("✔", ":)")) # Notify user about the server being ready
    def exit_handler(_s,_h):
        ui.info(ui.yellow, "Exiting..") # Inform the user about exiting
        sp_net.terminate() # Terminate the network manager
        for i in msp: # Iterate over match sub-processes
            i.terminate() # Terminate each of them 
        exit(0) # Exit..
    signal(SIGINT, exit_handler) # Setup the exit handler
    while(True): # Loop forever
        loop(sp_net, netp, qsp_net, max_p, max_m, mode) # Run the program loop
    # End of Section I

def loop(net, qm, qsp, max_p, max_m, mode):
    # Section II - Loop
    qm.send([spc.get_players.value]) # Pass on commond to send player list
    p = qm.recv() # Array for holding players in rooms and out of rooms
    for x in list(p[0]["room"].keys()): # i iterates through all rooms
        i=p[0]["room"][x] # Scope to the object for convience
        if(len(i)>=4): # If amount of participants in room is more than or equal to 4 participants
            msp.append(create_match(i, qsp, mode)) # Create a match with all participants in the room
            del p[0]["room"][x] # Delete the room object
            qm.send([spc.update_cc.value, p[0]]) # Send in a request to update the wait list
    if(len(p[0]["noroom"])>=4): # If noroom has more than or equal to 4 people
        e=sample(p[0]["noroom"], (int(len(p[0]["noroom"])/4)*4)) # Randomly choose groups of 4 people
        for q in range(int(len(p[0]["noroom"])/4)): # Iterate amount of groups present
            msp.append(create_match(e[q*4:(q+1)*4], qsp, mode)) # Create a match with all participants in the room
            for z in e[q*4:(q+1)*4]: # Iterate over all of the players
                del p[0]["noroom"][p[0]["noroom"].index(z)] # Delete the player from the player array
            qm.send([spc.update_cc.value, p[0]]) # Send in a request to update the wait list
    ui.info(ui.white, l.server_players.value, ui.yellow, "[", p[1], "/", max_p, "]", ui.white, l.server_matches.value, ui.yellow, "[", len(msp), "/", max_m, "]")
    sleep(2) # Sleep for 2 seconds
    # End of Section II

def create_match(players, qsp, m):
    # Section III - Create match
    sp = Process(target=match_proc, args=(players, qsp, m)) # Define the match sub-process
    sp.start() # Start up the sub-process
    return sp # Return the match sub-process
    # End of Section III

if __name__=="__main__":
    freeze_support()
    init()