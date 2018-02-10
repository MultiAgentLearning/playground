import random

from .envs.utility import DEFAULT_BLAST_STRENGTH, DEFAULT_BOMB_LIFE
from .envs.utility import Action, Item, GameType


class Agent(object):
    """Container to keep the agent state."""

    def __init__(self, agent_id, game_type):
        self.agent_id = agent_id
        self.ammo = 1
        self.is_alive = True
        self.blast_strength = DEFAULT_BLAST_STRENGTH
        self.can_kick = False
        self.speed = 0
        self.acceleration = 1
        self._init_max_speed = 1
        self.max_speed = 1
        self._current_direction = None
        if game_type == GameType.FFA:
            self.teammate = None
            self.enemies = [getattr(Item, 'Agent%d' % (id_+1))
                            for id_ in range(4) if id_ != agent_id]
        else:
            teammate_id = (agent_id + 2) % 4
            self.teammate = getattr(Item, 'Agent%d' % (teammate_id+1))
            self.enemies = [getattr(Item, 'Agent%d' % (id_+1))
                            for id_ in range(4) if id_ != agent_id and id_ != teammate_id]

    def maybe_lay_bomb(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bomb(self, self.position, DEFAULT_BOMB_LIFE, self.blast_strength)
        return None

    def incr_ammo(self):
        self.ammo += 1

    def get_next_position(self, direction):
        if direction != self._current_direction:
            speed = 0
        else:
            speed = self.speed

        speed += self.acceleration
        speed = max(speed, self.max_speed)

        row, col = self.position
        if Action(direction) == Action.Up:
            row -= speed
        elif Action(direction) == Action.Down:
            row += speed
        elif Action(direction) == Action.Left:
            col -= speed
        elif Action(direction) == Action.Right:
            col += speed
        return (row, col)

    def move(self, direction):
        # Reset the speed if we were going in the other direction.
        if direction != self._current_direction:
            self._current_direction = direction
            self.speed = 0

        self.position = self.get_next_position(direction)

    def stop(self):
        self.speed = 0

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
        self.can_kick = False
        self.speed = 0
        self.acceleration = 1
        self.max_speed = self._init_max_speed
        self._current_direction = None

    def pick_up(self, item):
        if item == Item.ExtraBomb:
            self.ammo += 1
        elif item == Item.IncrRange:
            self.blast_strength += 1
        elif item == Item.Kick:
            self.can_kick = True
        elif item == Item.Skull:
            if random.random() < .5:
                self.blast_strength = max(2, self.blast_strength - 1)
            else:
                self.ammo = max(1, self.ammo - 1)


class Bomb(object):
    """Container for the Bomb object."""

    def __init__(self, bomber, position, life, blast_strength):
        self.bomber = bomber
        self.position = position
        self._life = life
        self.blast_strength = blast_strength
        self.moving_direction = None

    def tick(self):
        self._life -= 1

    def move(self):
        row, col = self.position
        if self.moving_direction == Action.Up:
            row -= 1
        elif self.moving_direction == Action.Down:
            row += 1
        elif self.moving_direction == Action.Left:
            col -= 1
        elif self.moving_direction == Action.Right:
            col += 1
        self.position = (row, col)

    def stop(self):
        self.moving_direction = None

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

    def is_moving(self):
        return self.moving_direction is not None


class Flame(object):
    """Container for Flame object."""
    def __init__(self, position):
        self.position = position
        self._life = 2

    def tick(self):
        self._life -= 1

    def is_dead(self):
        return self._life == 0

