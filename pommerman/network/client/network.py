#!/usr/bin/env python
"""IonClient Network Manager

This file contains the Network class that can be used directly. It is also
thread-safe so feel free to run multiple network clients"""

import pommerman
import websocket
from . import constants
import rapidjson
import threading
import gzip
import numpy


class Network(object):
    """This class is responsible for handling communication b/w Client
    and Server"""

    def __init__(self, ip):
        """Arguments:  
        * ip: The IP of the server"""
        self.ws_ = websocket.create_connection(
            "ws://" + str(ip))
        self.lock = threading.Lock()

    def server_status(self):
        """Description: Retrieves the status of the server"""
        self._send(intent=constants.NetworkCommands.check.value)
        message_recieved = self._recieve()
        if message_recieved[
                "intent"] == constants.NetworkCommands.status_ok.value:
            return [message_recieved["players"], message_recieved["matches"]]
        elif message_recieved[
                "intent"] == constants.NetworkCommands.status_full.value:
            raise Exception(constants.Exceptions.net_server_full.value)
        else:
            raise Exception(constants.Exceptions.net_respond_fail.value)

    def join_list(self, room=False):
        """Description: Check if the server actually responds  
        Arguments:  
        * room: The room to be created/joined. If False, the public room will \
be joined, it should be a String"""
        if not room:
            self._send(intent=constants.NetworkCommands.match.value)
        else:
            self._send(
                intent=constants.NetworkCommands.room.value, room=str(room))
        message_recieved = self._recieve()
        if message_recieved[
                "intent"] == constants.NetworkCommands.status_full.value:
            if room:
                raise Exception(constants.Exceptions.room_full.value)
            else:
                raise Exception(constants.Exceptions.match_full.value)
        self.id = message_recieved["player_id"]
        self.mode = message_recieved["mode"]

    def wait_match(self):
        """Description: Wait for a response from the server regarding a match 
        request"""
        message_recieved = self._recieve()
        if message_recieved[
                "intent"] == constants.NetworkCommands.match_start.value:
            self.match_id = message_recieved["match_id"]

    def match_get(self):
        """Description: Get the next step of the match  
        Return values(Format: "0th element - Meaning - Other elements"):
        * 0 - Agent is still alive - OBS and Turn ID
        * 1 - Agent is dead - Nothing
        * 2 - Match has ended - Reward and agent item ID correlating to \
pommerman.constants.Items
        """
        self.lock.acquire()
        try:
            message_recieved = self.ws_.recv()
        except:
            raise Exception(constants.Exceptions.net_respond_fail.value)
        finally:
            self.lock.release()
        try:
            # Messages with normal match data are compressed using GZIP while
            # match end notifications aren't. So we move on to that if this
            # fails to decompress with gzip.
            message_decoded = rapidjson.loads(
                str(gzip.decompress(message_recieved), "utf-8"))
        except:
            try:
                message_decoded = rapidjson.loads(message_recieved)
                if message_decoded[
                        "intent"] == constants.NetworkCommands.match_end.value:
                    return [
                        2,
                        int(message_decoded["reward"]),
                        int(message_decoded["agent"])
                    ]
            except:
                raise Exception(constants.Exceptions.net_invalid_response.value)
        # Info: message_decoded - ["d"]=Dead, ["o"]=OBS, ["i"] = Turn ID
        if message_decoded["d"]:
            return [1]
        obs = message_decoded["o"]
        obs["teammate"] = pommerman.constants.Item[obs["teammate"]]
        # Note: If position is not tuple SimpleAgent *will* error out
        obs["position"] = tuple(obs["position"])
        for x, y in enumerate(obs["enemies"]):
            obs["enemies"][x] = pommerman.constants.Item[y]
        for i in ["board", "bomb_life", "bomb_blast_strength"]:
            obs[i] = numpy.asarray(obs[i])
        return [0, obs, message_decoded["i"]]

    def send_move(self, action, turn_id):
        """Description: Send the action to the server for playing out  
        Arguments:  
        * action: The action that has to be sent  
        * turn_id: The ID of the step taken by the server (To sync up the \
action of the agent and server)"""
        self._send(
            intent=constants.NetworkCommands.match_act.value,
            player_id=self.id,
            act=action,
            match_id=self.match_id,
            turn_id=turn_id)

    def get_replay(self, id):
        """Description: Send the action to the server for playing out  
        Arguments:  
        * id: The ID of the match to be replayed"""
        self._send(intent=constants.NetworkCommands.replay.value, replay_id=id)
        try:
            status, replay = rapidjson.loads(
                str(gzip.decompress(self.ws_.recv()), "utf-8"))
        except ValueError:
            raise Exception(constants.Exceptions.replay_notfound.value)
        if status == constants.NetworkCommands.status_ok.value:
            return replay
        else:
            raise Exception(constants.Exceptions.replay_notfound.value)

    def _send(self, **kwargs):
        self.lock.acquire()
        try:
            self.ws_.send(rapidjson.dumps(kwargs))
        except:
            raise Exception(constants.Exceptions.net_server_closed.value)
        finally:
            self.lock.release()

    def _recieve(self):
        self.lock.acquire()
        try:
            message_recieved = self.ws_.recv()
        except:
            if not self.ws_.connected:
                raise Exception(constants.Exceptions.net_server_closed.value)
            else:
                raise Exception(constants.Exceptions.net_invalid_response.value)
        finally:
            self.lock.release()
        try:
            return rapidjson.loads(message_recieved)
        except:
            raise Exception(constants.Exceptions.net_invalid_response.value)