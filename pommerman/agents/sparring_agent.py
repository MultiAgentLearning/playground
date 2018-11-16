import copy
import numpy as np
from pommerman import *
from . import BaseAgent
from .. import MCTS
from .. import constants
from .. import utility


class SparringAgent(BaseAgent):

    def __init__(self, sparrer_type, model=None):
        super().__init__()

        if sparrer_type == constants.SIMPLE_SPARRER:
            self.modelled_env = make('PommeTeamCompetition-v0', agent_list=[agents.SimpleAgent() for _ in range(4)])
        elif sparrer_type == constants.MODEL_SPARRER:
            # FIXME: may require changes
            self.modelled_env = make('PommeTeamCompetition-v0', agent_list=[agents.SmartAgent(model) for _ in range(4)])
        elif sparrer_type == constants.RANDOM_SPARRER:
            # FIXME: may require changes
            self.modelled_env = make('PommeTeamCompetition-v0', agent_list=[agents.RandomAgent() for _ in range(4)])
        else:
            raise ValueError('Invalid sparrer type')

        self.training_examples = []
        self.memory = None


    # def update_memory(self, agent_obs):
    #     """
    #     Update agent's memory of the board
    #     :param agent_obs: Agent's observation at the current timestep
    #     :return: None
    #     """
    #
    #     def _get_explosion_range(row, col, blast_strength_map):
    #         strength = int(blast_strength_map[row, col])
    #         indices = {
    #             'up': ([row - i, col] for i in range(1, strength)),
    #             'down': ([row + i, col] for i in range(strength)),
    #             'left': ([row, col - i] for i in range(1, strength)),
    #             'right': ([row, col + i] for i in range(1, strength))
    #         }
    #         return indices
    #
    #     # Note: all three 11x11 boards are numpy arrays
    #     if self.memory is None:
    #         self.memory = {
    #             'bomb_life': np.copy(agent_obs['bomb_life']),
    #             'bomb_blast_strength': np.copy(agent_obs['bomb_blast_strength']),
    #             'board': np.copy(agent_obs['board'])
    #         }
    #         return
    #
    #     # Update history by incrementing timestep by 1
    #     board = self.memory['board']
    #     bomb_life = self.memory['bomb_life']
    #     bomb_blast_strength = self.memory['bomb_blast_strength']
    #
    #     # Decrease bomb_life by 1
    #     original_bomb_life = np.copy(bomb_life)
    #     np.putmask(bomb_life, bomb_life > 0, bomb_life - 1)
    #
    #     # Find out which bombs are going to explode
    #     exploding_bomb_pos = np.logical_xor(original_bomb_life, bomb_life)
    #     non_exploding_bomb_pos = np.logical_and(bomb_life, np.ones_like(bomb_life))
    #     has_explosions = exploding_bomb_pos.any()
    #
    #     # Map to record which positions will become flames
    #     flamed_positions = np.zeros_like(board)
    #
    #     while has_explosions:
    #         has_explosions = False
    #         # For each bomb
    #         for row, col in zip(*exploding_bomb_pos.nonzero()):
    #             # For each direction
    #             for direction, indices in _get_explosion_range(row, col, bomb_blast_strength).items():
    #                 # For each location along that direction
    #                 for r, c in indices:
    #                     if not utility.position_on_board(board, (r, c)):
    #                         break
    #                     # Stop when reaching a wall
    #                     if board[r, c] == constants.Item.Rigid.value:
    #                         break
    #                     # Otherwise the position is flamed
    #                     flamed_positions[r, c] = 1
    #                     # Stop when reaching a wood
    #                     if board[r, c] == constants.Item.Wood.value:
    #                         break
    #
    #         # Check if other non-exploding bombs are triggered
    #         exploding_bomb_pos = np.zeros_like(exploding_bomb_pos)
    #
    #         for row, col in zip(*non_exploding_bomb_pos.nonzero()):
    #             if flamed_positions[row, col]:
    #                 has_explosions = True
    #                 exploding_bomb_pos[row, col] = True
    #                 non_exploding_bomb_pos[row, col] = False
    #
    #     # Update bomb_life map
    #     self.memory['bomb_life'] = np.where(flamed_positions == 0, bomb_life, 0)
    #     # Update bomb_strength map
    #     self.memory['bomb_blast_strength'] = np.where(flamed_positions == 0, bomb_blast_strength, 0)
    #
    #     # Update Board
    #     # If board from observation has fog value, do nothing &
    #     # keep original updated history.
    #     # Otherwise, overwrite history by observation.
    #     self.memory['board'] = np.where(flamed_positions == 0, self.memory['board'], constants.Item.Passage.value)
    #
    #     # Overlay agent's newest observations onto the memory
    #     obs_board = agent_obs['board']
    #     for r, c in zip(*np.where(obs_board != constants.Item.Fog.value)):
    #         # board[r, c] = obs_board[r, c] if obs_board[r, c] in self.memory_values else 0
    #         self.memory['board'][r, c] = obs_board[r, c]
    #         self.memory['bomb_life'][r, c] = agent_obs['bomb_life'][r, c]
    #         self.memory['bomb_blast_strength'][r, c] = agent_obs['bomb_blast_strength'][r, c]
    #
    #     # For invisible parts of the memory, only keep useful information
    #     for r, c in zip(*np.where(obs_board == constants.Item.Fog.value)):
    #         if self.memory['board'][r, c] not in self.memory_values:
    #             self.memory['board'][r, c] = constants.Item.Passage.value


    def act(self, obs, action_space):
        # Sparring agent won't need to act
        return constants.Action.Stop.value



    def simulate(self):
        """
        Agent simulates a game to generate training data
        :return: The training data of a game (i.e 1 episode)
        """
        done = False
        while not done:
            # All agents' observations
            agents_obs = self.modelled_env.get_observations()

            # self.update_memory(agents_obs[self.agent_id])
            self.memory = utility.update_agent_memory(self.memory, agents_obs[self.agent_id])

            # Perform MCTS from this agent's perspective
            action_prior = MCTS.perform_MCTS(self.modelled_env, self.agent_id, self.memory)
            sampled_action = np.random.choice(np.arange(len(action_prior)), p=action_prior)

            # Get all agents' actions (which depend on the sparring type)
            agents_actions = self.modelled_env.act(agents_obs)
            agents_actions[self.agent_id] = sampled_action

            # TODO: use Meng's obs -> model to make training example
            X = utility.combine_agent_obs_and_memory(self.memory, agents_obs[self.agent_id])
            y = action_prior

            self.training_examples.append((X, y, self.agent_id))
            _, _, done, _ = self.modelled_env.step(action=agents_actions)

        return self.training_examples