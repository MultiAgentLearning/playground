"""The Pommerman v3 Environment, which implements Sudden Death mode.

The game ends when any agent dies. In FFA, all other agents win. In any of the team
modes, the team with the most remaining players wins. If all players die at the same
time or the same number of players die on each time, the game ends in a tie. All
players/teams win if the game ends without anyone dying.
"""
from .. import constants
from .. import forward_model
from .. import utility
from . import v0


class Pomme(v0.Pomme):
    metadata = {
        'render.modes': ['human', 'rgb_array']
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_done(self):
        alive = [agent for agent in self._agents if agent.is_alive]
        alive_ids = sorted([agent.agent_id for agent in alive])
        if self._step_count >= self._max_steps:
            return True
        elif len(alive) < 4:
            return True
        return False

    def _get_info(self, done, rewards):
        if self._game_type == constants.GameType.FFA:
            alive = [agent for agent in self._agents if agent.is_alive]
            if done and len(alive) == 0:
                return {
                    'result': constants.Result.Tie,
                }
            elif done:
                return {
                    'result': constants.Result.Win,
                    'winners': [num for num, reward in enumerate(rewards) if reward == 1]
                }
            else:
                return {'result': constants.Result.Incomplete}
        elif self._game_type == constants.GameType.Team or \
                                self._game_type == constants.GameType.TeamRadio:
            alive = [agent for agent in self._agents if agent.is_alive]
            if done and len(alive) < 4:
                team1 = []
                team2 = []
                for agent in alive:
                    if agent.agent_id == 0 or agent.agent_id == 2:
                        team1.append(agent.agent_id)
                    else:
                        team2.append(agent.agent_id)
                if len(team1) == len(team2):
                    return {
                        'result': constants.Result.Tie,
                    }
                else:
                    return {
                        'result': constants.Result.Win,
                        'winners': [num for num, reward in enumerate(rewards) if reward == 1]
                    }
            else:
                return {'result': constants.Result.Incomplete}
        elif done:
            if rewards == [1]*4:
                return {'result': constants.Result.Tie}
            else:
                return {
                    'result': constants.Result.Win,
                    'winners': [num for num, reward in enumerate(rewards) if reward == 1]
                }
        else:
            return {'result': constants.Result.Incomplete}

    def _get_rewards(self):
        alive_agents = [num for num, agent in enumerate(self._agents) if agent.is_alive]
        if len(alive_agents) == 0:
            return [0]*4
        elif self._game_type == constants.GameType.FFA:
            ret = [-1]*4
            if len(alive_agents) > 0 or self._step_count >= self._max_steps:
                for num in alive_agents:
                    ret[num] = 1
            else:
                for num in alive_agents:
                    ret[num] = 0
            return ret
        elif self._game_type == constants.GameType.Team or \
                                self._game_type == constants.GameType.TeamRadio:
            team1 = []
            team2 = []
            for agentnum in alive_agents:
                if agentnum == 0 or agentnum == 2:
                    team1.append(agentnum)
                else:
                    team2.append(agentnum)
            if len(team1) == len(team2):
                return [0]*4
            else:
                if len(team1) > len(team2):
                    return [1, -1, 1, -1]
                else:
                    return [-1, 1, -1, 1]
        elif self._step_count >= self._max_steps:
            return [1]*4
        else:
            return [0]*4
