#!/usr/bin/env python
# IonClient Network Manager

# Imports
from asyncio import new_event_loop, set_event_loop, get_event_loop
from websockets import serve
from threading import Thread
from .constants import spc, nic
from time import time, sleep
from os import getcwd, path
from re import fullmatch
from gzip import compress
from rapidjson import loads, dumps, load
from json import JSONDecodeError
from uuid import uuid4

# Global variables
cc={"room":{}, "noroom":[]} # Concurrently looking for a match
ccpm={} # Stores websocket mappings to player integer
mpl={} # Stores a dict of dicts which have pipes with their respective players connected to match sub-processes
mp=0 # Max amount of concurrent players
mm=0 # Max amount of concurrent matches
tp=0 # Amount of seconds to wait before issuing the STOP action
lck=False # A pseudo-lock to manage threads (This is potentially the most primitive form of locks)
mode="" # This defines the mode of the game

# This function parses messages recieved by WebSocket
async def ws_handler(ws, pth):
    global lck # For some reason lck appears to be not defined even though it is as a global
    while(lck): # While lock isn't locked
        pass # Do nothing
    lck=True # Acquire the lock
    async for message in ws: # For messages recieved by ws
        try: # Try to..
            message = loads(message) # Decode a message as JSON
        except JSONDecodeError: # If the message cannot be decoded
            pass # Return nothing
        try: # Try to..
            if(message["i"]==nic.check.value): # If the intent of the message is to check
                await ws.send(dumps({"i":nic.s_ok.value, "p":len(ccpm), "m":len(mpl)})) # Return an okay
            elif(message["i"]==nic.match_act.value): # If the intent of the message was to pass on an action
                if(message["sid"]==mpl[message["u"]]["id"]): # Check if action is for current step
                    mpl[message["u"]]["act"][mpl[message["u"]]["pl"].index(message["id"])]=message["act"] # Set action in action array 
                    mpl[message["u"]]["recv"][mpl[message["u"]]["pl"].index(message["id"])]=True # Set the action recieved to True for that user
            elif(message["i"]==nic.replay.value): # If the intent was to retrieve a replay
                try: # Try to..
                    with open(path.join(path.join(getcwd(),"matches"),str(message["p"])+".json"), 'r') as f: # Open the file
                        # Note: Registry expression match comes after as it's an expensive operation so if it's done after opening the file the filename has to be valid
                        if(fullmatch("^[a-z0-9-]*$", message["p"])!=None): # Check if the file-name is valid
                            f=load(f) # Load the file into the variable
                            await ws.send(compress(bytes(dumps([nic.s_ok.value, f]), "utf8"))) # Return the data
                        else:
                            await ws.send(compress(bytes(dumps([nic.s_fail.value]), "utf8"))) # Return an error
                except: # If an exception occured
                    await ws.send(compress(bytes(dumps([nic.s_fail.value]), "utf8"))) # Return an error
            elif(len(ccpm)<mp and (message["i"]==nic.match.value or message["i"]==nic.room.value)): # If concurrent players are less than or equal to max concurrent players
                    u=str(uuid4()) # Generate a UUID
                    while u in ccpm: # If the UUID has collided generate a new one till no-collision is found
                        u=str(uuid4()) # Generate a UUID
                    ccpm[u]={"ws":ws} # Store the websocket object of the user in ccpm
                    if(message["i"]==nic.match.value): # If the intent of the message is to join a match
                        cc["noroom"].append(u) # Store the reference UUID of the user in cc
                        ccpm[u]["l"]=True # Set location of UUID to noroom (True)
                    elif(message["i"]==nic.room.value): # If the intent of the message is to join a room
                        if message["room"] in cc["room"]: # If room already exists
                            if len(cc["room"][message["room"]])<4: # If less than 4 people are in the room
                                cc["room"][message["room"]].append(u) # Add current user's UUID to room
                        else:
                            cc["room"][message["room"]]=[u]
                        ccpm[u]["l"]=False # Set location of UUID to room (False)
                        ccpm[u]["r"]=str(message["room"]) # Set room to the name of the room
                    await ws.send(dumps({"i":nic.s_reg.value, "id": u, "m": mode})) # Return data to the client
        except: # If parsing the message fails at any point
            pass # Then just pass
        lck=False # Release the lock
        sleep(0.0001) # Sleep for the a extremely small amount of time so the other thread can take the lock

# This functions handles almost everything else in the program
async def program_loop(port):
    global lck, cc # For some reason lck appears to be not defined even though it is as a global
    while(True): # Keep running this loop
        while(lck): # While lock isn't locked
            pass # Do nothing
        lck=True # Acquire the lock
        for uuid in list(ccpm.keys()): # Iterate over all users
            i=ccpm[uuid] # For convenience
            if i["ws"].closed: # If the connection was closed
                if(i["l"]==True): # If current user wasn't in a room
                    try: # Try to..
                        del cc["noroom"][cc["noroom"].index(uuid)] # Remove the UUID from the noroom list
                    except: # If an exception occured.
                        pass # Ignore the error
                elif(i["l"]==False): # If current user was in a room
                    try: # Try to..
                        del cc["room"][i["r"]][cc["room"][i["r"]].index(uuid)] # Remove the UUID from the room list
                    except: # If an exception occured.
                        pass # Ignore the error
                del ccpm[uuid] # Remove the player from the concurrent players list
        if qm.poll(): # If main pipe isn't empty
            q=qm.recv() # Get an object from it
            if(q[0]==spc.get_players.value): # If request is for getting concurrent players
                qm.send([cc, len(ccpm)]) # Return list of concurrent players to main proces
            elif(q[0]==spc.update_cc.value): # If request is updating the wait-list
                cc=q[1] # Set the wait-list to the value given by the main server
        if not qsp.empty(): # If sub-process queue isn't empty
            q=qsp.get() # Get an object from it
            mpl[q[2]]={"p": q[0],"pl":q[1], "u":q[2], "f":False, "d": False} # Add current object into mpl
            for i in q[1]: # Iterate over players in match
                if i in ccpm: # If player is in concurrent players list
                    await ccpm[i]["ws"].send(dumps({"i":nic.match_start.value, "u":q[2]})) # Send match start request with UUID of match
        for z in list(mpl.keys()): # Iterate through all matches
            i=mpl[z] # Variable for convenience
            if(i["p"].poll() and not i["f"]): # Check if pipe has data
                o=i["p"].recv() # Recieve data from pipe
                if(o[0]==spc.match_next.value): # If intent was to play out the next step of the match
                    i["f"]=not i["f"] # Flip the timeout switch 
                    i["act"]=[0, 0, 0, 0] # Create an action array
                    i["recv"]=[False, False, False, False] # Create an array that holds if actions are recieved from players 
                    i["time"]=time() # Set the timestamp
                    i["id"]=o[1] # Set the turn ID
                    for x, y in enumerate(i["pl"]): # Enumerate over players in match
                        if y in list(ccpm.keys()): # If player is in concurrent players list (ie: Not automatically disconnected)
                            try: # Try to..
                                await ccpm[y]["ws"].send(o[x+2]) # Send corresponding observations to players
                            except: # If an exception occured
                                pass # Ignore it
                        elif y not in ccpm: # If player is not in concurrent players list (ie: Automatically disconnected)
                            i["act"][x]=5 # Set the action to BOMB so the player will die
                if(o[0]==spc.match_end.value): # If intent was to end the match
                    i["d"]=True # Set current pipe up for deletion
                    for x, y in enumerate(i["pl"]): # Enumerate over players in match
                        if y in ccpm: # If player is in concurrent players list (ie: Not automatically disconnected)
                            await ccpm[y]["ws"].send(dumps({"i": nic.match_end.value, "r": o[1][x]})) # Send notification about match ending
            if i["f"]: # Check if the server is waiting for moves
                if (i["time"]+tp<time()) or all(i["recv"])==True: # If match-action timeout is exceeded then play the action out
                    i["p"].send(i["act"]) # Send action back to match sub-process
                    i["f"]=not i["f"] # Reset the timeout switch
            if i["d"]: # If the current pipe is set to be deleted
                i["p"].send("END") # Send an END so the match process will exit
                del mpl[z] # Delete the current pipe
        lck=False # Release the lock
        sleep(0.0001) # Sleep for the a extremely small amount of time so the other thread can take the lock

# Define Network Thread function
def thread(qm_, qsp_, port, mp_, mm_, mode_, tp_):
    global mp, mm, qm, qsp, mode, tp # Set locals to globals
    # Assign parameters to globals
    mp=mp_
    mm=mm_
    qm=qm_
    qsp=qsp_
    mode=mode_
    tp=tp_
    def run_server(port):
        set_event_loop(new_event_loop()) # We create a new event loop for the thread
        get_event_loop().run_until_complete(serve(ws_handler, 'localhost', port)) # Define secondary event-loop
        get_event_loop().run_forever() # Run secondary event-loop
    t=Thread(target=run_server, args=(port,)) # Run the network thread
    t.start() # Start up the thread
    get_event_loop().run_until_complete(program_loop(port)) # Define primary event-loop
    get_event_loop().run_forever() # Run primary event-loop
    t.join() # Join with the thread