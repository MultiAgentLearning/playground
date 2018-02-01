from collections import defaultdict
import random

import a
from a.pommerman.envs import utility


class TestAgent(a.agents.Agent):
    """This is a TestAgent. It is not meant to be submitted as playable.

    To do that, you would need to turn it into a DockerAgent. See the Docker folder for an example.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._my_bombs = []

    def act(self, obs, action_space):
        my_position = obs['position']
        board = obs['board']
        enemies = obs['enemies']
        items, dist, prev = self._djikstra(board, my_position)

        print("ACT: ")
        # print(items)
        # print(dist)
        # print(prev)

        # Move if we are in an unsafe place.
        unsafe_directions = self._directions_in_range_of_bomb(board, my_position, items, dist)
        if unsafe_directions:
            print('1')
            directions = self._find_safe_directions(board, my_position, unsafe_directions)
            return random.choice(directions).value

        # Lay pomme if we are adjacent to an enemy.
        if self._is_adjacent_enemy(items, dist, enemies) and self._has_bomb(obs):
            print('2')
            return utility.Action.Bomb.value

        # Move towards an enemy if there is one within three reachable spaces.
        direction = self._near_enemy(my_position, items, dist, prev, enemies, 3)
        if direction is not None:
            print('3')
            return direction.value

        # Move towards a good item if there is one within two reachable spaces.
        direction = self._near_item(my_position, items, dist, prev, 2)
        if direction is not None:
            print('4')
            return direction.value

        # Lay a bomb if we are within two spaces of a wooden wall.
        if self._near_wood(my_position, items, dist, prev, 2) and self._has_bomb(obs):
            print('5')
            return utility.Action.Bomb.value

        # Choose a random but valid direction.
        valid_directions = self._get_valid_directions(board, my_position)
        print('6')
        return random.choice(valid_directions).value

    @staticmethod
    def _djikstra(board, my_position):
        items = defaultdict(list)
        dist = {}
        prev = {}
        Q = []

        for r in range(len(board)):
            for c in range(len(board[0])):
                position = (r, c)
                if board[position] != utility.Item.Fog.value:
                    # Value bigger than possible.
                    dist[position] = len(board)**2
                    prev[position] = []
                    Q.append(position)

        dist[my_position] = 0

        while Q:
            Q = sorted(Q, key=lambda position: dist[position])

            position = Q.pop(0)
            x, y = position

            if utility.position_is_passable(board, position):
                val = dist[(x, y)] + 1
                for row, col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_position = (row + x, col + y)
                    if not utility.position_on_board(board, new_position):
                        continue

                    if val < dist[new_position]:
                        dist[new_position] = val
                        prev[new_position] = position

            item = utility.Item(int(board[position]))
            items[item].append(position)

        return items, dist, prev

    @staticmethod
    def _directions_in_range_of_bomb(board, my_position, items, dist):
        ret = []

        bombs = items.get(utility.Item.Bomb, [])
        if not bombs:
            return ret

        x, y = my_position
        for position in bombs:
            bomb_range = int((board[position] - utility.Item.Bomb.value)*10)
            if dist[position] > bomb_range:
                continue

            if my_position == position:
                # We are on a bomb. All directions are bad. Pick one of them and move.
                return [
                    utility.Action.Right,
                    utility.Action.Left,
                    utility.Action.Up,
                    utility.Action.Down,
                ]
            elif x == position[0]:
                if y < position[1]:
                    # Bomb is right.
                    ret.append(utility.Action.Right)
                else:
                    # Bomb is left.
                    ret.append(utility.Action.Left)
            elif y == position[1]:
                if x < position[0]:
                    # Bomb is up.
                    ret.append(utility.Action.Up)
                else:
                    # Bomb is down.
                    ret.append(utility.Action.Down)

        return ret

    @staticmethod
    def _find_safe_directions(board, my_position, unsafe_directions):
        x, y = my_position
        disallowed = [] # The directions that will go off the board.
        safe = []

        for row, col, direction in [
                (-1, 0, utility.Action.Down),
                (1, 0, utility.Action.Up),
                (0, -1, utility.Action.Left),
                (0, 1, utility.Action.Right)
        ]:
            position = (x + row, y + col) 

            # Don't include any direction that will go off of the board.
            if not utility.position_on_board(board, position):
                disallowed.append(direction)

            # Don't include any direction that we know is unsafe.
            if direction in unsafe_directions:
                continue

            if utility.position_is_passable(board, position) or utility.position_is_fog(board, position):
                safe.append(direction)

        if not safe:
            # We don't have any safe directions, so return something that is allowed.
            return [k for k in unsafe_directions if k not in disallowed]

        if not safe:
            # We don't have ANY directions. So return the stop choice.
            return [utility.Action.Stop]

        return safe

    @staticmethod
    def _is_adjacent_enemy(items, dist, enemies):
        for enemy in enemies:
            for position in items.get(enemy, []):
                if dist[position] == 1:
                    return True
        return False

    @staticmethod
    def _has_bomb(obs):
        return obs['ammo'] >= 1

    @staticmethod
    def _nearest_position(dist, objs, items, radius):
        nearest = None
        dist_to = max(dist.values())

        for obj in objs:
            for position in items.get(obj, []):
                d = dist[position]
                if d <= radius and d <= dist_to:
                    nearest = position
                    dist_to = d

        return nearest

    @staticmethod
    def _get_direction_towards_position(my_position, position, prev):
        if not position:
            return None

        next_position = position
        while prev[next_position] != my_position:
            next_position = prev[next_position]

        return utility.get_direction(my_position, next_position)

    @classmethod
    def _near_enemy(cls, my_position, items, dist, prev, enemies, radius):
        nearest_enemy_position = cls._nearest_position(dist, enemies, items, radius)
        return cls._get_direction_towards_position(my_position, nearest_enemy_position, prev)

    @classmethod
    def _near_item(cls, my_position, items, dist, prev, radius):
        objs = [
            utility.Item.ExtraBomb,
            utility.Item.IncrRange,
            utility.Item.Kick
        ]
        nearest_item_position = cls._nearest_position(dist, objs, items, radius)
        return cls._get_direction_towards_position(my_position, nearest_item_position, prev)

    @classmethod
    def _near_wood(cls, my_position, items, dist, prev, radius):
        objs = [utility.Item.Wood]
        nearest_item_position = cls._nearest_position(dist, objs, items, radius)
        return cls._get_direction_towards_position(my_position, nearest_item_position, prev)

    @staticmethod
    def _get_valid_directions(board, my_position):
        ret = [utility.Action.Stop]
        x, y = my_position
        for row, col, direction in [
                (-1, 0, utility.Action.Down),
                (1, 0, utility.Action.Up),
                (0, -1, utility.Action.Left),
                (0, 1, utility.Action.Right)
        ]:

            # Don't include any direction that will go off of the board.
            position = (x + row, y + col)
            if utility.position_on_board(board, position) and utility.position_is_passable(board, position):
                ret.append(direction)
        return ret
