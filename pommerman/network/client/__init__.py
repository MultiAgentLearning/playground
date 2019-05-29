#!/usr/bin/env python
"""IonClient Entry Point  

This library allows playing of matches on network via the WebSockets protocol.  
Functions:  
init() - If you want to run the application normally  
intent(network) - If you want to pass a pre-existing network object but want to
prompt the user about what they want to do  
match(network, room=False, agent=False, ui_en=False) - If you want 
to start a match directly  
replay(network, id=False, ui_en=False) - If you want to start a replay directly  
"""

import ui
from . import constants
from .network import Network
import signal
import sys
import os
import pommerman
import importlib
import gym
import numpy


def _exit_handler(_s=None, _h=None):
    """Arguments:  
    * _s: Unused argument  
    * _h: Unused argument  
    Description: Handle exiting the application"""
    ui.info(ui.yellow, "Exiting..")
    exit(0)


def init():
    """Description: Starts up the application normally by asking the user about
    the server they want to connect to"""
    if ui.ask_yes_no(constants.Strings.server_prompt.value):
        domain = ui.ask_string(constants.Strings.server_ip.value)
        if domain is None:
            ui.fatal(constants.Exceptions.invalid_ip.value)
    else:
        domain = "play.pommerman.com:5050"
    ui.info(
        constants.Strings.server_connecting_p1.value,
        ui.yellow,
        constants.Strings.server_connecting_p2.value,
        ui.reset,
        constants.Strings.server_connecting_p3.value,
    )
    network = Network(domain)
    try:
        status = network.server_status()
    except Exception as e:
        ui.fatal(e)
    signal.signal(signal.SIGINT, _exit_handler)
    ui.info(
        constants.Strings.server_connected.value,
        ui.yellow,
        constants.Strings.server_players.value,
        str(status[0]) + ",",
        constants.Strings.server_matches.value,
        status[1],
    )
    intent(network)


def _agent_prompt():
    """Description: Prompt the user to import their agent"""
    sys.path.append(os.getcwd())
    agent = importlib.import_module(ui.ask_string(constants.Strings.match_import.value))
    agent_class = ui.ask_string(constants.Strings.match_class_name.value)
    if agent_class not in agent.__dir__():
        ui.fatal(constants.Strings.error_invalid_class.value)
    agent = getattr(agent, agent_class)
    if getattr(agent, "act"):
        ui.info(ui.green, constants.Strings.match_agent_success.value)
    return agent


def intent(network):
    """Description: This creates a prompt for the user where they can choose to:  
    * Play a match  
    * Create/Join a room  
    * Replay a match  
    * Exit the application  
    Arguments:   
    * network: An `network`(pommerman.network.ion_client.network) object  
    """
    i = ui.ask_choice(
        constants.Strings.intent.value,
        [
            constants.Strings.intent_match.value,
            constants.Strings.intent_room.value,
            constants.Strings.intent_replay.value,
            constants.Strings.intent_exit.value,
        ],
    )
    if i == constants.Strings.intent_match.value:
        agent = _agent_prompt()
        match(network, agent=agent, ui_en=True)
    elif i == constants.Strings.intent_room.value:
        room = str(ui.ask_string(constants.Strings.room_code.value))
        agent = _agent_prompt()
        match(network, room=room, agent=agent, ui_en=True)
    elif i == constants.Strings.intent_replay.value:
        replay(network, ui_en=True)
    elif i == constants.Strings.intent_exit.value:
        exit(0)


def match(network, room=False, agent=False, ui_en=False):
    """Description: This facilitates playing a match  
    Arguments:  
    * network: An `network`(pommerman.network.ion_client.network) object  
    * room: If String, The room to be created/joined. If False, the public \
room will be joined  
    * agent: The class of the agent should be a derivative of BaseAgent  
    * ui_en: If the UI is enabled or disabled (This also controls if exception \
are raised or not)
    Returns: Array [reward, match_id]"""
    agent = agent()
    if ui_en:
        ui.info(ui.yellow, constants.Strings.server_comm.value)
    try:
        network.join_list(room)
    except Exception as e:
        if ui_en:
            ui.fatal(e)
        raise e
    if ui_en:
        ui.info(constants.Strings.match_variant.value, ui.yellow, network.mode)
        ui.info(ui.yellow, constants.Strings.match_wait.value)
    try:
        network.wait_match()
    except Exception as e:
        if ui_en:
            ui.fatal(e)
        raise e
    if ui_en:
        ui.info(constants.Strings.match_run.value, "#" + network.match_id)
    for mode in pommerman.constants.GameType:
        if mode.name in network.mode:
            agent.init_agent(
                id=0, game_type=mode
            )  # We always use ID as 0 as the server doesn't return it
    while True:
        try:
            match_obj = network.match_get()
        except Exception as e:
            if ui_en:
                ui.fatal(e)
            raise e
        # match_obj[0] is the intent: 0 = OBS, 1 = Agent Dead, 2 = Match End
        if match_obj[0] is 0:
            action = agent.act(match_obj[1], gym.spaces.Discrete(6))
            try:
                network.send_move(action, match_obj[2])
            except Exception as e:
                if ui_en:
                    ui.fatal(e)
                raise e
        elif match_obj[0] is 2:
            agent.episode_end(reward=match_obj[1])
            if ui_en:
                if match_obj[1] == 1:
                    ui.info(constants.Strings.match_won.value)
                if match_obj[1] == -1:
                    ui.info(constants.Strings.match_loss_draw.value)
                ui.info(
                    constants.Strings.match_agent.value,
                    ui.yellow,
                    pommerman.constants.Item(match_obj[2]).name,
                )
            else:
                return [match_obj[1], network.match_id]
            break
    ui.info(constants.Strings.match_replay.value, ui.yellow, network.match_id)
    if ui.ask_yes_no(constants.Strings.match_ask_replay.value):
        replay(network, network.match_id)
    else:
        intent(network)


def replay(network, id=False, ui_en=False):
    """Description: This replays a particular match  
    Arguments:  
    * network: An `network`(pommerman.network.ion_client.network) object  
    * id: The ID of a match to be played. If False, the user is prompted about \
it.  
    * ui_en: If the UI is enabled or disabled (This also controls if exception are\
raised or not)"""
    if not id and ui_en:
        id = ui.ask_string(constants.Strings.replay_prompt.value)
        if id is None:
            ui.fatal(constants.Strings.error_invalid_id.value)
        id = str(id)
    if id[0] == "#":
        id = id[1:]
    ui.info(
        constants.Strings.server_replay_p1.value,
        ui.yellow,
        "#" + str(id),
        ui.reset,
        constants.Strings.server_replay_p2.value,
    )
    try:
        replay_obj = network.get_replay(id)
    except Exception as e:
        if ui_en:
            ui.fatal(e)
        raise e
    if ui_en:
        ui.info(constants.Strings.replay_start.value, ui.yellow, "#" + str(id))
    env = pommerman.make(
        replay_obj["mode"],
        [
            pommerman.agents.BaseAgent(),
            pommerman.agents.BaseAgent(),
            pommerman.agents.BaseAgent(),
            pommerman.agents.BaseAgent(),
        ],
    )
    env.reset()
    env._board = numpy.array(replay_obj["board"])
    # Note: Render FPS is set to 30 as it'll be smoother
    env._render_fps = 30
    for i in replay_obj["actions"]:
        env.render()
        reward, done = env.step(i)[1:3]
        if done:
            break
    if reward != replay_obj["reward"]:
        if ui_en:
            ui.info(ui.yellow, constants.Exceptions.replay_no_reward.value)
        else:
            raise Exception(constants.Exceptions.replay_no_reward.value)
    env.close()
    if ui_en:
        ui.info(ui.yellow, constants.Strings.replay_end.value)
    intent(network)


if __name__ == "__main__":
    init()
