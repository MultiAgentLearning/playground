from .envs.utility import *


class Agent(object):
    """Container to keep the agent state."""

    def __init__(self, agent_id, start_position=None):
        self.agent_id = agent_id
        self.start_position = start_position
        self.position = start_position
        self.ammo = 1
        self.is_alive = True
        self.blast_strength = DEFAULT_BLAST_STRENGTH

    def maybe_lay_bomb(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bomb(self, self.position, DEFAULT_BOMB_LIFE, self.blast_strength)
        return None

    def incr_ammo(self):
        self.ammo += 1

    def move(self, direction):
        row, col = self.position
        if Direction(direction) == Direction.UP:
            row -= 1
        elif Direction(direction) == Direction.DOWN:
            row += 1
        elif Direction(direction) == Direction.LEFT:
            col -= 1
        elif Direction(direction) == Direction.RIGHT:
            col += 1
        self.position = (row, col)

    def in_range(self, exploded_map):
        row, col = self.position
        return exploded_map[row][col] == 1

    def die(self):
        self.is_alive = False

    def set_start_position(self, start_position):
        self.start_position = start_position

    def reset(self):
        self.position = self.start_position
        self.ammo = 1
        self.is_alive = True
        self.blast_strength = DEFAULT_BLAST_STRENGTH


class Bomb(object):
    def __init__(self, bomber, position, life, blast_strength):
        self.bomber = bomber
        self.position = position
        self._life = life
        self.blast_strength = blast_strength

    def step(self):
        self._life -= 1

    def exploded(self):
        return self._life == 0

    def explode(self):
        row, col = self.position
        indices = {
            'up': ([row - i, col] for i in range(1, self.blast_strength)),
            'down': ([row + i, col] for i in range(self.blast_strength)),
            'left': ([row, col - i] for i in range(1, self.blast_strength)),
            'right': ([row, col + i] for i in range(1, self.blast_strength))
        }
        return indices

    def in_range(self, exploded_map):
        row, col = self.position
        return exploded_map[row][col] == 1

