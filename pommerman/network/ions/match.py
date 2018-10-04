#!/usr/bin/env python
# IonClient Match handler

# Imports
from multiprocessing import Queue, Pipe
from .constants import spc
from uuid import uuid4
from os import listdir, makedirs
from numpy import array
from rapidjson import dumps, dump
from gzip import compress
from enum import Enum
from numpy import ndarray, uint8, int64
from copy import copy
import pommerman
BaseAgent=pommerman.agents.BaseAgent

# Finds a unique UUID
def unique_uuid(dir):
    while(True):
        u = str(uuid4())[:10] # Generate a UUID
        try: # Try to list everything in the 'dir' directory
            l=listdir(dir) # List everything in the 'dir' directory
        except FileNotFoundError: # If that fails with a FileNotFoundError
            makedirs(dir) # Create a new directory 'dir'
            l=[] # The newly created directory should be empty
        if not u+".json" in l: # If we cannot find a similar UUID in the 'dir' directory
            return u # Return the UUID

# Resolve classes before JSON serialization
def resolve_classes(i):
    if(isinstance(i, tuple)): # If object is tuple
        i=list(i) # Convert to list because tuples are immutable
    for x, v in enumerate(i): # Enumerate over iterator
        if(isinstance(i, dict)): # If object is dict change it's format
            x=v # Make x the key
            v=i[x] # Make v the value
        if(hasattr(v, '__iter__') and not isinstance(i[x], str) and not isinstance(i[x], ndarray)): # If current item is iterator except if it's a string or ndarray
            i[x]=resolve_classes(v) # Iterate over iterable classes
        elif(isinstance(v, Enum)): # If item is Enum
            i[x]=str(v.name) # Resolve the value of the Enum
        elif(isinstance(v, ndarray)): # If item is numpy array
            i[x]=v.tolist() # Convert it into a numpy array
        elif(isinstance(v, uint8) or isinstance(v, int64)): # If item is uint8 or int64
            i[x]=int(v) # Convert numpy uint8 or int64 to a python integer
    return i # Return the created array

# Define Match Thread function
def thread(pl, qsp, mode):
    u=unique_uuid("matches") # Generates a unique UUID
    env = pommerman.make(mode, [BaseAgent(),BaseAgent(),BaseAgent(),BaseAgent()]) # Creates a pommerman environment with inert agents
    net, net_end = Pipe() # Create a pipe
    qsp.put([net_end, pl, u]) # Send down one end of the pipe to the network application
    obs=env.reset() # Reset the pommerman environment
    record={"board":array(env._board, copy=True).tolist(),"actions":[], "mode":str(mode)} # JSON structure of actions
    done=False # This flips on the match ending
    while not done: # Run event loop
        o=resolve_classes(obs.copy()) # Resolve all classes to make them serializable with JSON
        t_id=str(uuid4())[:5] # Create a UUID as the turn ID
        try: # Try to..
            net.send([spc.match_next.value, t_id, compress(bytes(dumps({"o":o[0], "i":t_id}), "utf8")), compress(bytes(dumps({"o":o[1], "i":t_id}), "utf8")), compress(bytes(dumps({"o":o[2], "i":t_id}), "utf8")), compress(bytes(dumps({"o":o[3], "i":t_id}), "utf8"))]) # Send obs to network manager
            act=net.recv() # Get actions from network manager
        except: # If an exception occured
            act=[0,0,0,0] # Ignore it and issue everyone a STOP rather than crashing...
        record["actions"].append(array(act, copy=True).tolist()) # Add current action to action list for recording
        obs, rew, done = env.step(act)[:3] # Forward the game with playing out the actions
    record["reward"]=rew # Store the end reward
    env.close() # Close the environment
    with open("./matches/"+u+".json", "w") as file: # Open file with UUID in write-mode
        dump(record, file) # Dump match data into file
    net.send([spc.match_end.value, rew]) # Send match end out to clients
    net.recv() # Wait for pipe to be deleted from network process