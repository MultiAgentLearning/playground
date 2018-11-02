#!/usr/bin/env python
"""IonServer Network handler

This contains functions responsible Server-Client communication 
(You shouldn't use this file directly due to the very specialized 
interactions required for it to function in addition to parameters 
i.e: Pipes, Queues. This is the reason for the simple docstrings
for functions)"""

import asyncio
import websockets
import threading
import time
from . import constants
import os
import re
import gzip
import rapidjson
import uuid

CONCURRENTLY_LOOKING = {
    "room": {},
    "noroom": []
}  # This holds the IDs of players concurrently looking for a room
PLAYER_WS = {}  # This stores the mapping from player ID to the websocket object
MATCH_PROCESS = {}  # This holds pipes to match processes
MAX_PLAYERS = 0
PIPE_MAIN = False  # This holds the queue (Main-proc <-> Network-proc)
QUEUE_SUBPROC = False  # This holds the queue (Subproc <-> Network-proc)
MODE = ""
STOP_TIMEOUT = 0


async def message_parse(message, websocket):
    """Parse the messages recieved from the clients"""
    if message["intent"] is constants.NetworkCommands.check.value:
        await websocket.send(
            rapidjson.dumps({
                "intent":
                constants.NetworkCommands.status_ok.value,
                "players":
                len(PLAYER_WS),
                "matches":
                len(MATCH_PROCESS)
            }))
    elif message["intent"] is constants.NetworkCommands.match_act.value:
        if message["turn_id"] == MATCH_PROCESS[message["match_id"]]["turn_id"]:
            # Note: The statements below assign the action to the respective players
            MATCH_PROCESS[message["match_id"]]["act"][
                MATCH_PROCESS[message["match_id"]]["players"].index(
                    message["player_id"])] = message["act"]
            MATCH_PROCESS[message["match_id"]]["recv"][MATCH_PROCESS[message[
                "match_id"]]["players"].index(message["player_id"])] = True
    elif message["intent"] is constants.NetworkCommands.replay.value:
        try:
            with open(
                    os.path.join(
                        os.path.join(os.getcwd(), "matches"),
                        str(message["replay_id"]) + ".json"), 'r') as f:
                # Note: Registry expression match comes after as it's an expensive operation as compared to file I/O
                if re.fullmatch("^[a-z0-9-]*$",
                                message["replay_id"]) is not None:
                    f = rapidjson.load(f)
                    await websocket.send(
                        gzip.compress(
                            bytes(
                                rapidjson.dumps([
                                    constants.NetworkCommands.status_ok.value, f
                                ]), "utf8")))
                else:
                    await websocket.send(
                        gzip.compress(
                            bytes(
                                rapidjson.dumps([
                                    constants.NetworkCommands.status_fail.value
                                ]), "utf8")))
        except:
            await websocket.send(
                gzip.compress(
                    bytes(
                        rapidjson.dumps(
                            [constants.NetworkCommands.status_fail.value]),
                        "utf8")))
    elif message["intent"] in [
            constants.NetworkCommands.match.value,
            constants.NetworkCommands.room.value
    ]:
        if len(PLAYER_WS) >= MAX_PLAYERS:
            await websocket.send(
                rapidjson.dumps({
                    "intent":
                    constants.NetworkCommands.status_full.value
                }))
            return
        uuid_ = str(uuid.uuid4())
        while uuid_ in PLAYER_WS:
            uuid_ = str(uuid.uuid4())
        PLAYER_WS[uuid_] = {"ws": websocket}
        if message["intent"] is constants.NetworkCommands.match.value:
            CONCURRENTLY_LOOKING["noroom"].append(uuid_)
            PLAYER_WS[uuid_]["noroom"] = True
        elif message["intent"] is constants.NetworkCommands.room.value:
            if message["room"] in CONCURRENTLY_LOOKING["room"]:
                if len(CONCURRENTLY_LOOKING["room"][message["room"]]) <= 4:
                    CONCURRENTLY_LOOKING["room"][message["room"]].append(uuid_)
                else:
                    await websocket.send(
                        rapidjson.dumps({
                            "intent":
                            constants.NetworkCommands.status_full.value
                        }))
                    return
            else:
                CONCURRENTLY_LOOKING["room"][message["room"]] = [uuid_]
            PLAYER_WS[uuid_]["noroom"] = False
            PLAYER_WS[uuid_]["room"] = str(message["room"])
        await websocket.send(
            rapidjson.dumps({
                "intent":
                constants.NetworkCommands.status_reg.value,
                "player_id":
                uuid_,
                "mode":
                MODE
            }))


async def ws_handler(websocket, pth=None):  # pylint: disable=unused-argument
    """Handle the messages recieved by WebSocket (pth is not required but still\
returned by the 'websockets' library)"""
    try:
        async for message in websocket:
            try:
                await message_parse(rapidjson.loads(message), websocket)
            except:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass


async def program_loop():
    """Handles other network-related function"""
    global CONCURRENTLY_LOOKING
    while (True):
        try:
            for uuid_ in list(PLAYER_WS.keys()):
                i = PLAYER_WS[uuid_]
                if not i["ws"].open:
                    if i["noroom"] is True:
                        try:
                            del CONCURRENTLY_LOOKING["noroom"][CONCURRENTLY_LOOKING[
                                "noroom"].index(uuid_)]
                        except:
                            pass
                    elif i["noroom"] is False:
                        try:
                            del CONCURRENTLY_LOOKING["room"][i["room"]][
                                CONCURRENTLY_LOOKING["room"][i["room"]].index(
                                    uuid_)]
                        except:
                            pass
                    try:
                        del PLAYER_WS[uuid_]
                    except:
                        pass
            if PIPE_MAIN.poll():
                queue_msg = PIPE_MAIN.recv()
                if queue_msg[0] is constants.SubprocessCommands.get_players.value:
                    PIPE_MAIN.send(
                        [CONCURRENTLY_LOOKING,
                         len(PLAYER_WS),
                         len(MATCH_PROCESS)])
                elif queue_msg[0] is constants.SubprocessCommands.update_cc.value:
                    CONCURRENTLY_LOOKING = queue_msg[1]
            if not QUEUE_SUBPROC.empty():
                queue_msg = QUEUE_SUBPROC.get()
                MATCH_PROCESS[queue_msg[2]] = {
                    "pipe": queue_msg[0],
                    "players": queue_msg[1],
                    "match_id": queue_msg[2],
                    "free": False,
                    "delete": False
             }
                for i in queue_msg[1]:
                    if i in PLAYER_WS:  # If the players didn't quits during matching
                        await PLAYER_WS[i]["ws"].send(
                            rapidjson.dumps({
                                "intent":
                                constants.NetworkCommands.match_start.value,
                                "match_id":
                                queue_msg[2]
                            }))
            for key in list(MATCH_PROCESS.keys()):
                value = MATCH_PROCESS[key]
                if value["pipe"].poll() and not value["free"]:
                    pipe_msg = value["pipe"].recv()
                    if pipe_msg[0] == constants.SubprocessCommands.match_next.value:
                        value["free"] = True
                        value["act"] = [0, 0, 0, 0]
                        value["recv"] = [False, False, False, False]
                        value["time"] = time.time()
                        value["turn_id"] = pipe_msg[1]
                        value["alive"] = pipe_msg[3]
                        for x, y in enumerate(value["players"]):
                            if y in list(PLAYER_WS.keys()):
                                try:
                                    await PLAYER_WS[y]["ws"].send(pipe_msg[2][x])
                                except:
                                    pass
                            elif y not in PLAYER_WS:
                                value["act"][x] = 5
                    if pipe_msg[0] is constants.SubprocessCommands.match_end.value:
                        value["delete"] = True
                        for x, y in enumerate(value["players"]):
                            if y in PLAYER_WS:
                                await PLAYER_WS[y]["ws"].send(
                                    rapidjson.dumps({
                                        "intent":
                                        constants.NetworkCommands.match_end.value,
                                        "reward":
                                        pipe_msg[1][x],
                                        "agent":
                                        10 + x
                                    }))
                if value["free"]:
                    if value["time"] + STOP_TIMEOUT < time.time(
                    ) or value["recv"].count(True) == value["alive"]:
                        value["pipe"].send(value["act"])
                        value["free"] = False
                if value["delete"]:
                    value["pipe"].send("END")
                    del MATCH_PROCESS[key]
        finally:
            time.sleep(0.0001)  # Sleep for a while so other threads get the GIL


def _run_server(port):
    """Handles running the websocket thread"""
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(ws_handler, 'localhost', port))
    asyncio.get_event_loop().run_forever()


def thread(pipe_main, queue_subproc, port, max_players, mode, stop_timeout):
    """Creates a network thread"""
    # Note: Multiple threads are used so globals are used to share data b/w them
    global MAX_PLAYERS, PIPE_MAIN, QUEUE_SUBPROC, MODE, STOP_TIMEOUT
    MAX_PLAYERS = max_players
    PIPE_MAIN = pipe_main
    QUEUE_SUBPROC = queue_subproc
    MODE = mode
    STOP_TIMEOUT = stop_timeout
    ws_thread = threading.Thread(target=_run_server, args=(port,))
    ws_thread.start()
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(program_loop())
    asyncio.get_event_loop().run_forever()
    ws_thread.join()
