from collections import defaultdict
import random

import numpy as np

from . import BaseAgent
from ..envs import utility


class DummyAgent(BaseAgent):
    """This agent starts off dead. For use in 1v1, 1v2, and 2v1."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_alive = False
        self._agent_type = 'dummy'
