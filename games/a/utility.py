from enum import Enum

from pyglet.window import key
import ruamel.yaml as yaml
# TODO: Remove the dependency on TF.
import tensorflow as tf 


class KeyInput(Enum):
    NULL = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SPACE = 5

KEY_INPUT = {'curr': 0}
def get_key_control(ty):
    def on_key_press(k, mod):
        global KEY_INPUT
        KEY_INPUT['curr'] = {
            key.UP: 1,
            key.DOWN: 2,
            key.LEFT: 3,
            key.RIGHT: 4,
            key.SPACE: 5,
        }.get(k)

    def on_key_release(k, mod):
        global KEY_INPUT
        KEY_INPUT['curr'] = 0

    return on_key_press, on_key_release


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


import contextlib


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
