#!/usr/bin/env python
"""IonServer Match handler

This contains functions responsible for playing matches 
(You shouldn't use this file directly due to the very specialized 
interactions required for it to function in addition to parameters 
i.e: Pipes, Queues)"""

import multiprocessing
from . import constants
import uuid
import os
import rapidjson
import gzip
import enum
import pommerman
import numpy


def unique_uuid(dir):
    """Generates a unique UUID and checks for collision with files within the
    specified directory (So we don't override a pre-existing file)"""
    try:
        ls_dir = os.listdir(dir)
    except FileNotFoundError:
        os.makedirs(dir)
        ls_dir = []
    uuid_ = str(uuid.uuid4())[:10]
    while uuid_ + ".json" in ls_dir:
        uuid_ = str(uuid.uuid4())[:10]
    return uuid_


def resolve_classes(i):
    """Resolves observation into JSONable types by looping over every element
    in it"""
    if isinstance(i, tuple):
        i = list(i)
    for key, value in enumerate(i):
        if isinstance(i, dict):
            key = value
            value = i[key]
        if hasattr(value, '__iter__') and not isinstance(
                i[key], str) and not isinstance(i[key], numpy.ndarray):
            i[key] = resolve_classes(value)
        elif isinstance(value, enum.Enum):
            i[key] = str(value.name)
        elif isinstance(value, numpy.ndarray):
            i[key] = value.tolist()
        elif isinstance(value, numpy.uint8) or isinstance(value, numpy.int64):
            i[key] = int(value)
    return i


def thread(players, queue_subproc, mode):
    """Handles running of the match loop"""
    uuid_ = unique_uuid("matches")
    base_agent = pommerman.agents.BaseAgent
    env = pommerman.make(
        mode,
        [base_agent(), base_agent(),
         base_agent(), base_agent()])
    net, net_end = multiprocessing.Pipe()
    queue_subproc.put([net_end, players, uuid_])
    obs = env.reset()
    record = {
        "board": numpy.array(env._board, copy=True).tolist(),
        "actions": [],
        "mode": str(mode)
    }
    done = False
    while not done:
        obs_res = resolve_classes(obs.copy())
        turn_id = str(uuid.uuid4())[:5]
        try:
            obs_bytes = []
            for key, value in enumerate(obs_res):
                if 10 + key in obs[0]["alive"]:
                    obs_bytes.append(
                        gzip.compress(
                            bytes(
                                rapidjson.dumps({
                                    "o": value,  # o = obs
                                    "i": turn_id,  # i = Turn ID
                                    "d": False  # d = Dead
                                }),
                                "utf8")))
                else:
                    obs_bytes.append(
                        gzip.compress(
                            bytes(
                                rapidjson.dumps({
                                    "d": True  # d = Dead
                                }),
                                "utf8")))
            net.send([
                constants.SubprocessCommands.match_next.value, turn_id,
                obs_bytes,
                len(obs[0]["alive"])
            ])
            act = net.recv()
        except:
            act = [0, 0, 0, 0]
        record["actions"].append(numpy.array(act, copy=True).tolist())
        obs, rew, done = env.step(act)[:3]
    record["reward"] = rew
    env.close()
    with open("./matches/" + uuid_ + ".json", "w") as file:
        rapidjson.dump(record, file)
    net.send([constants.SubprocessCommands.match_end.value, rew])
    net.recv()
    exit(0)
