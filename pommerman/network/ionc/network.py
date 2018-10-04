#!/usr/bin/env python
# IonClient Network Manager

# Imports
import asyncio
from pommerman import constants
import websocket as wsl
from .constants import nic
from rapidjson import dumps, loads
from threading import Lock
from gzip import decompress 
from numpy import asarray

# Define Network Class
class network(object):
    def __init__(self, ip):
        self.ws = wsl.create_connection("ws://"+str(ip), enable_multithread=True) # Connect to IP
        self.lock = Lock() # Create a lock for network functions
    def check(self):
        self.lock.acquire() # Acquire the lock
        self.ws.send(dumps({"i":nic.check.value})) # Send a check message to verify if the server is okay
        try: # Try to..
            m=loads(self.ws.recv()) # Wait for recieving a message and decode it using rapidjson
            self.lock.release() # Release the lock
            if(m["i"]==nic.s_ok.value): # If the status was successful
                return [True, m["p"], m["m"]] # If it was successful return [True]
            return [False, "e_respond_fail"] # Fail with connection respond error
        except: # If it was unsuccessful..
            self.lock.release() # Release the lock
            return [False, "e_connect_fail"] # Fail with connection error
    def join_list(self, room=False):
        self.lock.acquire() # Acquire the lock
        if not room:
            self.ws.send(dumps({"i":nic.match.value})) # Send request to server about joining match waiting list
        else:
            self.ws.send(dumps({"i":nic.room.value, "room":room})) # Send request to server about joining match waiting list in a specific room
        self.lock.release() # Release the lock
        u=loads(self.ws.recv()) # Get user info from server
        self.id=u["id"] # Set self.id to the id given by the server
        self.mode=u["m"] # Set mode to the server game-mode
    def waitm(self):
        self.lock.acquire() # Acquire the lock
        r=loads(self.ws.recv()) # Recieve for data from server
        if(r["i"]==nic.match_start.value): # If the intent of the message was to start a match
            self.m_id=r["u"] # Set match UUID to the one recieved from the server
        self.lock.release() # Release the lock
    def match_get(self):
        self.lock.acquire() # Acquire the lock
        m=self.ws.recv() # Recieve a message from the server
        self.lock.release() # Release the lock
        try: # Try to...
            r=loads(str(decompress(m),"utf-8")) # Recieve data and decode it
        except: # If an exception occured..
            try: # Try to...
                m=loads(m) # Try loading the message as a JSON message
            except: # If an exception occured..
                return [False, "w_no_recv"] # Return just False indicating that there was an error
            if(m["i"]==nic.match_end.value): # If the message was actually a match end request
                return [False, int(m["r"])] # Return False indicating match is over with the agent reward
            else: # If the intent was something else
                return [False, "w_no_recv"] # Return just False indicating that there was an error
        obs=r["o"] # Scope into r to get obs
        obs["teammate"]=constants.Item[obs["teammate"]] # Change the teammate property back into an Enum
        obs["position"]=tuple(obs["position"]) # Convert the list to a tuple
        for x, y in enumerate(obs["enemies"]): # Iterate over all enemies
            obs["enemies"][x]=constants.Item[y] # Change the Enum value into an Enum object
        for i in ["board","bomb_life","bomb_blast_strength"]: # Iterate through all 2D lists
            obs[i]=asarray(obs[i]) # Convert them into numpy arrays
        return [obs, r["i"]] # Return the observations and step ID
    def send_move(self, action, step_id):
        self.lock.acquire() # Acquire the lock
        try: # Try to..
            self.ws.send(dumps({"i":nic.match_act.value, "id": self.id, "act": action, "u": self.m_id, "sid": step_id})) # Send a check message to verify if the server is okay
        except: # If an exception occured
            self.lock.release() # Release the lock
            if self.ws.connected: # If the connection is still open
                pass # Ignore the error
            else:
                return [False, "e_server_closed"] # Return an error
        self.lock.release() # Release the lock
        return [True] # Return a True
    def get_replay(self,id):
        self.lock.acquire() # Acquire the lock
        self.ws.send(dumps({"i":nic.replay.value, "p":id})) # Send a request to retrieve the UUID to the server
        self.lock.release() # Release the lock
        m=loads(str(decompress(self.ws.recv()),"utf-8")) # Parse the response from the server
        if(m[0]==nic.s_ok.value): # If the replay was successfully retrieved
            return [True, m[1]] # Return the replay data
        else: # Else..
            return [False, "e_replay_notfound"] # Return an error