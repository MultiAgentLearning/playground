import a
import random

    
class TestAgent(a.agents.Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._my_bombs = []

    def act(self, obs):
        if self._in_range_of_bomb(obs):
            directions = self._find_safe_directions(obs)
            return random.choice(directions)

        if self._is_touching_enemy(obs) and self._has_bomb(obs):
            return lay_bomb()

        direction = closest_reachable_enemy(obs)
        if direction is not None:
            return direction

        direction = closest

    @staticmethod
    def _in_range_of_bomb(obs):
        pass

    @staticmethod
    def _is_touching_enemy(obs):
        pass

    @staticmethod
    def _has_bomb(obs):
        return obs['ammo'] >= 1

    @staticmethod
    def _closest_reachable_enemy(obs):
        pass



