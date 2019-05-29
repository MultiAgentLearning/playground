#!/usr/bin/env python
"""IonServer - This library allows playing of matches on network via the
WebSockets protocol.  
Functions:  
init() - If you want to run the application normally  
run(max_players, max_matches, port, timeout, mode, ui_en=True, 
exit_handler=True) - If you want to programatically launch the server with
predefined parameters"""

import ui
import multiprocessing
from . import constants
from . import network
from . import match
import time
import random
import signal
import pommerman

MATCH_SUBPROCESS = []


def _exit_handler(subprocess_net):
    """Description: Return the exit handler with a reference to the subprocess_net
    variable."""

    def exit_handler(_s, _h):
        """Description: Handle exiting the application."""
        ui.info(ui.yellow, "Exiting..")
        subprocess_net.terminate()
        for i in MATCH_SUBPROCESS:
            i.terminate()
        exit(0)

    return exit_handler


def init():
    """Description: Initiate the application by asking questions."""
    ui.info(ui.yellow, constants.Strings.sever_starting.value)
    port = int(ui.ask_string(constants.Strings.server_port.value))
    max_players = int(ui.ask_string(constants.Strings.server_maxp.value))
    if max_players < 4:
        # If the maximum players allowed on the server is less than 4
        # which is the minimum required for a pommerman match then
        # notify the user about that and quit.
        ui.fatal(ui.yellow, constants.Strings.server_playercount_too_low.value)
    modes = []
    for i in pommerman.configs.__dir__():
        if i[-4:] == "_env":
            id = getattr(pommerman.configs, i)()["env_id"]
            if id[-2:] != "v2":
                modes.append(id)
    timeout = float(ui.ask_string(constants.Strings.server_timeout.value))
    mode = str(ui.ask_choice(constants.Strings.server_mode.value, modes))
    run(port, max_players, timeout, mode, ui_en=True, exit_handler=True)


def run(port,
        max_players,
        timeout,
        mode,
        max_matches=False,
        ui_en=False,
        exit_handler=False):
    """Description: This function is responsible for running the server.  
    Arguments:  
    * port: The port used by the server  
    * max_players: The maximum amount of concurrent players  
    * timeout: (In Seconds) The time to wait before issuing the STOP action  
    * mode: The flavor of pommerman  
    * max_matches: The maximum amount of concurrent matches (If not defined this \
is set to int(max_players/4))
    * ui_en: If True, UI is enabled else UI is disabled  
    * exit_handler: If True, the exit handler is set else the exit handler \
isn't set"""
    netpipe, rnetpipe = multiprocessing.Pipe()
    netqueue = multiprocessing.Queue()
    subprocess_net = multiprocessing.Process(
        target=network.thread,
        args=(rnetpipe, netqueue, port, max_players, mode, timeout), daemon=True)
    subprocess_net.start()
    if not max_matches:
        max_matches = int(max_players / 4)
    if exit_handler:
        signal.signal(signal.SIGINT, _exit_handler(subprocess_net))
    if ui_en:
        ui.info(ui.yellow, constants.Strings.server_ready.value, ui.white,
                ui.Symbol("✔", ":)"))
    while True:
        netpipe.send([constants.SubprocessCommands.get_players.value])
        concurrent_list, num_players, num_matches = netpipe.recv()
        if int(num_matches) < max_matches:
            for x in list(concurrent_list["room"].keys()):
                i = concurrent_list["room"][x]
                if len(i) >= 4:
                    MATCH_SUBPROCESS.append(_create_match(i, netqueue, mode))
                    del concurrent_list["room"][x]
            if len(concurrent_list["noroom"]) >= 4:
                e = random.sample(concurrent_list["noroom"],
                                  (int(len(concurrent_list["noroom"]) / 4) * 4))
                for group in range(int(len(concurrent_list["noroom"]) / 4)):
                    MATCH_SUBPROCESS.append(
                        _create_match(e[group * 4:(group + 1) * 4], netqueue,
                                      mode))
                    for player in e[group * 4:(group + 1) * 4]:
                        del concurrent_list["noroom"][concurrent_list["noroom"]
                                                      .index(player)]
            netpipe.send(
                [constants.SubprocessCommands.update_cc.value, concurrent_list])
        if ui_en:
            ui.info(
                "\033[2K\r",
                ui.white,
                constants.Strings.server_players.value,
                ui.yellow,
                "[",
                num_players,
                "/",
                max_players,
                "]",
                ui.white,
                constants.Strings.server_matches.value,
                ui.yellow,
                "[",
                num_matches,
                "/",
                max_matches,
                "]",
                end="")
        for process in tuple(MATCH_SUBPROCESS):
            if not process.is_alive():
                MATCH_SUBPROCESS.remove(process)
        time.sleep(2)


def _create_match(players, queue_subproc, mode):
    """Description: This function is responsible for creating a match"""
    subprocess = multiprocessing.Process(
        target=match.thread, args=(players, queue_subproc, mode), daemon=True)
    subprocess.start()
    return subprocess


if __name__ == "__main__":
    multiprocessing.freeze_support()
    init()
