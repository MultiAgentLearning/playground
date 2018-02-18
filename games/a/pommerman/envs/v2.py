"""The Pommerman v2 Environment, which implements radio communication across the agents.

The communication works by allowing each agent to send a vector of radio_num_words (default = 2) from a vocabulary
of size radio_vocab_size (default = 8) to its teammate each turn. These vectors are passed into the observation
stream for each agent.
"""
from gym import spaces
import numpy as np

from . import utility
from . import v0


class Pomme(v0.Pomme):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : utility.RENDER_FPS
    }

    def __init__(self, *args, **kwargs):
        self._radio_vocab_size = kwargs.get('radio_vocab_size')
        self._radio_num_words = kwargs.get('radio_num_words')
        if (self._radio_vocab_size and not self._radio_num_words) or (not self._radio_vocab_size and self._radio_num_words):
            assert("Please provide both radio_vocab_size and radio_num_words to use the Radio environment.")

        self._radio_from_agent = {
            agent: (0, 0) for agent in [utility.Item.Agent0, utility.Item.Agent1, utility.Item.Agent2, utility.Item.Agent3]
        }
        super().__init__(*args, **kwargs)

    def _set_action_space(self):
        self.action_space = spaces.Tuple(tuple([spaces.Discrete(6)] + [spaces.Discrete(self._radio_vocab_size)]*self._radio_num_words))

    def _set_observation_space(self):
        # The observations (total = board_size^2 + 9):
        # - all of the board (board_size^2)
        # - agent's position (2)
        # - num ammo (1)
        # - blast strength (1)
        # - can_kick (0 or 1)
        # - teammate (one of {0, Agent.values}). If 0, then empty.
        # - enemies (three of {0, Agent.values}). If 0, then empty.
        # - radio (radio_vocab_size * radio_num_words)
        min_obs = [0]*(self._board_size**2 + 9)
        max_obs = [len(utility.Item)]*self._board_size**2 + [self._board_size]*2 + [10, 10, 1] + [3]*4
        min_obs.extend([0]*self._radio_vocab_size*self._radio_num_words)
        max_obs.extend([1]*self._radio_vocab_size*self._radio_num_words)
        self.observation_space = spaces.Box(np.array(min_obs), np.array(max_obs))

    def get_observations(self):
        observations = super().get_observations()
        for obs in observations:
            obs['message'] = self._radio_from_agent[obs['teammate']]

        self.observations = observations
        return observations

    def step(self, actions):
        personal_actions = [action[0] for action in actions]
        radio_actions = [action[1:] for action in actions]

        for radio_action, agent in zip(radio_actions, self._agents):
            if not agent.is_alive:
                radio_action = (0, 0)
            else:
                radio_action = np.clip(radio_action, 1, 8).astype(np.uint8)
            self._radio_from_agent[getattr(utility.Item, 'Agent%d' % agent.agent_id)] = radio_action

        return super().step(personal_actions)

    def act(self, obs):
        ret = []
        for agent in self._agents:
            if agent.agent_id == self.training_agent:
                continue
            if agent.is_alive:
                action = agent.act(obs[agent.agent_id], action_space=self.action_space)
                if type(action) == int:
                    action = [action] + [0, 0]
                assert(type(action) == list)

                # So humans can stop the game.
                if action[0] == 6:
                    time.sleep(300)
                ret.append(action)
            else:
                ret.append([utility.Action.Stop.value, 0, 0])
        return ret
