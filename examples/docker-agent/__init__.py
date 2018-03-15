"""Top-level Docker module"""

import os
import logging
import logging.config

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logging.yml")

with open(CONFIG_PATH) as f:
    logging.config.dictConfig(yaml.load(f))

