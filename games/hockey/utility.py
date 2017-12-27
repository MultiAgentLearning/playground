import contextlib
import os

import ruamel.yaml as yaml
import tensorflow as tf


# These are categoryBits used in the Box2D fixtures for detecting collisions.
SKIP = 0x0010
GOAL1 = 0x0020
GOAL2 = 0x0030
PUCK = 0x0040
WALL = 0x0050
TEAM1 = 0x0060
TEAM2 = 0x0070
CATEGORY_BITS = [SKIP, GOAL1, GOAL2, PUCK, WALL, TEAM1, TEAM2]


def get_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2 - y1)**2 + (x2 - x1)**2)


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def random_actions(action_space):
    """Creates a set of random actions for testing.

    Args:
      action_space: A gym action_space

    Returns:
      a set of random actions following the format described in action_space.
    """
    pass


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
        tf.logging.info(message.format(config.logdir))
        tf.gfile.MakeDirs(config.logdir)
        config_path = os.path.join(config.logdir, 'config.yaml')
        with tf.gfile.FastGFile(config_path, 'w') as file_:
            yaml.dump(config, file_, default_flow_style=False)
    else:
        message = (
            'Start a new run without storing summaries and checkpoints since no '
            'logging directory was specified.')
        tf.logging.info(message)
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
    if not config_path or not tf.gfile.Exists(config_path):
        message = (
            'Cannot resume an existing run since the logging directory does not '
            'contain a configuration file.')
        raise IOError(message)
    with tf.gfile.FastGFile(config_path, 'r') as file_:
        config = yaml.load(file_)
    message = 'Resume run and write summaries and checkpoints to {}.'
    tf.logging.info(message.format(config.logdir))
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
