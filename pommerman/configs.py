"""Configs module: Add game configs here.

Besides game configs, also includes helpers for handling configs, e.g. saving
and loading them.

NOTE: If you add a new config to this, add a _env on the end of the function
in order for it to be picked up by the gym registrations.
"""
import contextlib
import logging
import os

import ruamel.yaml as yaml

from . import constants
from . import envs
from . import characters


def ffa_competition_env():
    """Start up a FFA config with the competition settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.FFA
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeFFACompetition-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': constants.RENDER_FPS,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def ffa_competition_fast_env():
    """Start up a FFA config with the competition settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.FFA
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeFFACompetitionFast-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': 1000,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def team_competition_env():
    """Start up a Team config with the competition settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.Team
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeTeamCompetition-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': constants.RENDER_FPS,
        'agent_view_size': constants.AGENT_VIEW_SIZE,
        'is_partially_observable': True,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def team_competition_fast_env():
    """Start up a Team config with the competition settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.Team
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeTeamCompetitionFast-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': 1000,
        'agent_view_size': constants.AGENT_VIEW_SIZE,
        'is_partially_observable': True,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def ffa_v0_fast_env():
    """Start up a FFA config with the default settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.FFA
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeFFAFast-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': 1000,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def ffa_v1_env():
    """Start up a collapsing FFA config with the default settings."""
    env = envs.v1.Pomme
    game_type = constants.GameType.FFA
    env_entry_point = 'pommerman.envs.v1:Pomme'
    env_id = 'PommeFFA-v1'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'first_collapse': constants.FIRST_COLLAPSE,
        'max_steps': constants.MAX_STEPS,
        'render_fps': constants.RENDER_FPS,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def team_v0_env():
    """Start up a team config with the default settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.Team
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeTeam-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': constants.RENDER_FPS,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def team_v0_fast_env():
    """Start up a team config with the default settings."""
    env = envs.v0.Pomme
    game_type = constants.GameType.Team
    env_entry_point = 'pommerman.envs.v0:Pomme'
    env_id = 'PommeTeamFast-v0'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'render_fps': 2000,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def radio_v2_env():
    """Start up a team radio config with the default settings."""
    env = envs.v2.Pomme
    game_type = constants.GameType.TeamRadio
    env_entry_point = 'pommerman.envs.v2:Pomme'
    env_id = 'PommeRadio-v2'
    env_kwargs = {
        'game_type': game_type,
        'board_size': constants.BOARD_SIZE,
        'agent_view_size': constants.AGENT_VIEW_SIZE,
        'num_rigid': constants.NUM_RIGID,
        'num_wood': constants.NUM_WOOD,
        'num_items': constants.NUM_ITEMS,
        'max_steps': constants.MAX_STEPS,
        'is_partially_observable': True,
        'radio_vocab_size': constants.RADIO_VOCAB_SIZE,
        'radio_num_words': constants.RADIO_NUM_WORDS,
        'render_fps': constants.RENDER_FPS,
        'env': env_entry_point,
    }
    agent = characters.Bomber
    return locals()


def save_config(config, logdir=None):
    """Save a new configuration by name.

    If a logging directory is specified, is will be created and the configuration
    will be stored there. Otherwise, a log message will be printed.

    Args:
      config: Configuration object.
      logdir: Location for writing summaries and checkpoints if specified.

    Returns:
      Configuration object.
    """
    if logdir:
        with config.unlocked:
            config.logdir = logdir
        message = 'Start a new run and write summaries and checkpoints to {}.'
        logging.info(message.format(config.logdir))
        os.makedirs(config.logdir)
        config_path = os.path.join(config.logdir, 'config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    else:
        message = (
            'Start a new run without storing summaries and checkpoints since no '
            'logging directory was specified.')
        logging.info(message)
    return config


def load_config(logdir):
    """Load a configuration from the log directory.

    Args:
      logdir: The logging directory containing the configuration file.

    Raises:
      IOError: The logging directory does not contain a configuration file.

    Returns:
      Configuration object.
    """
    config_path = logdir and os.path.join(logdir, 'config.yaml')
    if not config_path or not os.path.exists(config_path):
        message = (
            'Cannot resume an existing run since the logging directory does not '
            'contain a configuration file.')
        raise IOError(message)
    with open(config_path, 'r') as file_:
        config = yaml.load(file_)
    message = 'Resume run and write summaries and checkpoints to {}.'
    logging.info(message.format(config.logdir))
    return config


class AttrDict(dict):
    """Wrap a dictionary to access keys as attributes."""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        super(AttrDict, self).__setattr__('_mutable', False)

    def __getattr__(self, key):
        # Do not provide None for unimplemented magic attributes.
        if key.startswith('__'):
            raise AttributeError
        return self.get(key, None)

    def __setattr__(self, key, value):
        if not self._mutable:
            message = "Cannot set attribute '{}'.".format(key)
            message += " Use 'with obj.unlocked:' scope to set attributes."
            raise RuntimeError(message)
        if key.startswith('__'):
            raise AttributeError("Cannot set magic attribute '{}'".format(key))
        self[key] = value

    @property
    @contextlib.contextmanager
    def unlocked(self):
        super(AttrDict, self).__setattr__('_mutable', True)
        yield
        super(AttrDict, self).__setattr__('_mutable', False)

    def copy(self):
        return type(self)(super(AttrDict, self).copy())
