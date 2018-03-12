from collections import defaultdict
from enum import Enum
import itertools
import random

import numpy as np

from a.pommerman.characters import Flame

RENDER_FPS = 15
BOARD_SIZE = 13
NUM_RIGID = 50
NUM_WOOD = 50
NUM_ITEMS = int(NUM_WOOD/2)
AGENT_VIEW_SIZE = 4
TIME_LIMIT = 3000
HUMAN_FACTOR = 32
DEFAULT_BLAST_STRENGTH = 3
DEFAULT_BOMB_LIFE = 25
AGENT_COLORS = [[231,76,60], [46,139,87], [65,105,225], [238,130,238]] # color for each of the 4 agents
ITEM_COLORS = [[240,248,255], [128,128,128], [210,180,140], [255, 153, 51], [241, 196, 15], [141, 137, 124]]
ITEM_COLORS += [(153, 153, 255), (153, 204, 204), (97, 169, 169), (48, 117, 117)] # ExtraBomb, IncrRange, etc. 
FIRST_COLLAPSE = 500 # If using V1, the first step at which the board starts to collapse.
MAX_STEPS = 2500
RADIO_VOCAB_SIZE = 8
RADIO_NUM_WORDS = 2


class Item(Enum):
    Passage = 0
    Rigid = 1
    Wood = 2
    Bomb = 3
    Flames = 4
    Fog = 5
    ExtraBomb = 6 # adds ammo.
    IncrRange = 7 # increases the blast_strength
    Kick = 8 # can kick bombs by touching them.
    Skull = 9 # randomly either reduces ammo, (capped at 1), reduces blast_strength (capped at 2), or increases blast_strength by 2.
    Agent0 = 10
    Agent1 = 11
    Agent2 = 12
    Agent3 = 13


class GameType(Enum):
    # 1v1v1v1. You submit an agent and it competes against other single agents.
    FFA = 1 
    # 2v2: You submit one agent. It is matched up randomly with another agent and together take on two other similarly matched agents.
    Team = 2
    # 2v2: You submit two agents. They are matched up against two other agents. Each team passes discrete communications to each other.
    TeamRadio = 3


class Action(Enum):
    Stop = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4
    Bomb = 5
    Pause = 6 # This pauses the game for 5 seconds.


class Result(Enum):
    Win = 0
    Loss = 1
    Tie = 2
    Incomplete = 3


class InvalidAction(Exception):
    pass


def make_board(size, num_rigid=0, num_wood=0):
    """Make the random but symmetric board.

    The numbers refer to the Item enum in utility. This is:
     0 - passage
     1 - rigid wall
     2 - wood wall
     3 - bomb
     4 - flames
     5 - fog
     6 - extra bomb item
     7 - extra firepower item
     8 - kick
     9 - skull
     10 - 13: agents

    Args:
      size: The dimension of the board, i.e. it's sizeXsize.
      num_rigid: The number of rigid walls on the board. This should be even.
      num_wood: Similar to above but for wood walls.

    Returns:
      board: The resulting random board.
    """
    assert(num_rigid % 2 == 0)
    assert(num_wood % 2 == 0)

    def lay_wall(value, num_left):
        x, y = random.sample(coordinates, 1)[0]
        coordinates.remove((x, y))
        coordinates.remove((y, x))
        board[x, y] = value
        board[y, x] = value
        num_left -= 2
        return num_left

    if num_rigid is None:
        num_rigid = size
    _num_rigid = num_rigid
    _num_wood = num_wood

    # Initialize everything as a passage.
    board = np.ones((size, size)).astype(np.uint8) * Item.Passage.value

    # Gather all the possible coordinates to use for walls.
    coordinates = set([(x, y) for x, y in itertools.product(range(size), range(size)) if x != y])

    # Set the players down. Exclude them from coordinates.
    board[1, 1] = Item.Agent0.value
    board[size-2, 1] = Item.Agent1.value
    board[size-2, size-2] = Item.Agent2.value
    board[1, size-2] = Item.Agent3.value
    agents = [(1, 1), (size-2, 1), (1, size-2), (size-2, size-2)]
    for position in agents:
        if position in coordinates:
            coordinates.remove(position)

    # Exclude breathing room on either side of the agents.
    for i in range(2, 4):
        coordinates.remove((1, i))
        coordinates.remove((i, 1))
        coordinates.remove((1, size-i-1))
        coordinates.remove((size-i-1, 1))
        coordinates.remove((size-2, size-i-1))
        coordinates.remove((size-i-1, size-2))
        coordinates.remove((i, size-2))
        coordinates.remove((size-2, i))

    # Lay down the rigid walls.
    while num_rigid > 0:
        num_rigid = lay_wall(Item.Rigid.value, num_rigid)

    # Lay down the wooden walls.
    while num_wood > 0:
        num_wood = lay_wall(Item.Wood.value, num_wood)

    # Make sure it's possible for the agents to reach each other.
    if not is_accessible(board, agents):
        # TODO: This is excessive. Fix it.
        # print('This board has unreachable passages or agents. Re-making...')
        return make_board(size, _num_rigid, _num_wood)

    return board


def make_items(board, num_items):
    item_positions = {}
    while num_items > 0:
        row = random.randint(0, len(board)-1)
        col = random.randint(0, len(board[0])-1)
        if board[row, col] != Item.Wood.value:
            continue
        if (row, col) in item_positions:
            continue

        item_positions[(row, col)] = random.choice([
            Item.ExtraBomb, Item.IncrRange, Item.Kick, Item.Skull
        ]).value
        num_items -= 1
    return item_positions


def is_accessible(board, agent_positions):
    """Return true if this board is accessible.

    That means two thigns:
    1. All of the agents can reach each other.
    2. Every passage can be reached.
    """
    seen = set()
    agent_position = agent_positions.pop()
    passage_positions = np.where(board == Item.Passage.value)
    positions = agent_positions
    positions.extend(list(zip(passage_positions[0], passage_positions[1])))
    # wood_positions = np.where(board == Item.Wood.value)
    # positions.extend(list(zip(wood_positions[0], wood_positions[1])))

    Q = [agent_position]
    while Q:
        row, col = Q.pop()
        for (i, j) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            next_position = (row+i, col+j)
            if next_position in seen:
                continue
            if not position_on_board(board, next_position):
                continue
            if position_is_rigid(board, next_position):
                continue

            if next_position in positions:
                positions.pop(positions.index(next_position))
                if not len(positions):
                    return True

            seen.add(next_position)
            Q.append(next_position)
    return False
    

def is_valid_direction(board, position, direction, invalid_values=None):
    row, col = position
    invalid_values = invalid_values or [item.value for item in [Item.Rigid, Item.Wood]]

    if Action(direction) == Action.Stop:
        return True

    if Action(direction) == Action.Up:
        return row - 1 >= 0 and board[row-1][col] not in invalid_values
    
    if Action(direction) == Action.Down:
        return row + 1 < len(board) and board[row+1][col] not in invalid_values
    
    if Action(direction) == Action.Left:
        return col - 1 >= 0 and board[row][col-1] not in invalid_values

    if Action(direction) == Action.Right:
        return col + 1 < len(board[0]) and board[row][col+1] not in invalid_values

    raise InvalidAction("We did not receive a valid direction: ", direction)


def position_is_powerup(board, position):
    item_values = [
        item.value for item in [Item.ExtraBomb, Item.IncrRange, Item.Kick, Item.Skull]
    ]
    return board[position] in item_values


def position_is_bomb(board, position):
    return board[position] == Item.Bomb.value


def position_is_passage(board, position):
    return board[position] == Item.Passage.value


def position_is_rigid(board, position):
    return board[position] == Item.Rigid.value


def position_is_agent(board, position):
    return board[position] in [
        Item.Agent0.value,
        Item.Agent1.value,
        Item.Agent2.value,
        Item.Agent3.value
    ]


def position_is_enemy(board, position, enemies):
    return Item(board[position]) in enemies


def agent_value(id_):
    return getattr(Item, 'Agent%d' % id_).value


def position_is_passable(board, position, enemies):
    return any([position_is_agent(board, position), position_is_powerup(board, position) or position_is_passage(board, position)]) and not position_is_enemy(board, position, enemies)


def position_is_fog(board, position):
    return board[position] == Item.Fog.value


def position_on_board(board, position):
    x, y = position
    return all([
        len(board) > x,
        len(board[0]) > y,
        x >= 0,
        y >= 0
    ])


def get_direction(position, next_position):
    """Gets the action value that goes from position --> next_position. Assumes that they are adjacent."""
    x, y = position
    nx, ny = next_position
    if x == nx:
        if y < ny:
            return Action.Right
        else:
            return Action.Left
    elif y == ny:
        if x < nx:
            return Action.Down
        else:
            return Action.Up
    raise InvalidAction("We did not receive a valid position transition.")


def get_next_position(position, direction):
    x, y = position
    if direction == Action.Right:
        return (x, y+1)
    elif direction == Action.Left:
        return (x, y-1)
    elif direction == Action.Down:
        return (x+1, y)
    elif direction == Action.Up:
        return (x-1, y)
    elif direction == Action.Stop:
        return (x, y)
    raise InvalidAction("We did not receive a valid direction.")


def make_np_float(feature):
    return np.array(feature).astype(np.float32)


###
### Forward Modeling.
###

class ForwardModel(object):
    """Class for helping with the [forward] modeling. Abstracts out the game state."""

    def run(self, num_times, board, agents, bombs, items, flames, is_partially_observable, agent_view_size, action_space, is_communicative=False):
        """Run the forward model.

        Args:
          num_times: The number of times to run it for. This is a maximum and it will stop early if we reach a done.
          board: The board state to run it from.
          agents: The agents to use to run it.
          bombs: The starting bombs.
          items: The starting items.
          flames: The starting flames.
          is_partially_observable: Whether the board is partially observable or not. Only applies to TeamRadio.
          agent_view_size: If it's partially observable, then the size of the square that the agent can view.
          action_space: The actions that each agent can take.
          is_communicative: Whether the action depends on communication observations as well.

        Returns:
          steps: The list of step results, which are each a dict of "obs", "next_obs", "reward", "action".
          board: Updated board.
          agents: Updated agents, same models though.
          bombs: Updated bombs.
          items: Updated items.
          flames: Updated flames.
          done: Whether we completed the game in these steps.
          info: The result of the game if it's completed.
        """
        steps = []
        for _ in num_times:
            obs = self.get_observations(board, agents, bombs, is_partially_observable, agent_view_size)
            actions = self.act(agents, obs, action_space, is_communicative=is_communicative)
            board, agents, bombs, items, flames = self.step(actions, board, agents, bombs, items, flames)
            next_obs = self.get_observations(board, agents, bombs, is_partially_observable, agent_view_size)
            reward = self.get_rewards(agents, game_type, step_count, max_steps)
            done = self.get_done(agents, game_type, step_count, max_steps, training_agent)
            info = self.get_info(done, rewards, game_type, agents)

            steps.append({
                "obs": obs,
                "next_obs": next_obs,
                "reward": reward,
                "actions": actions,
            })
            if done:
                break
        return steps, board, agents, bombs, items, flames, done, info

    @staticmethod
    def act(agents, obs, action_space, is_communicative=False):
        """Returns actions for each agent in this list.

        Args:
          agents: A list of agent objects.
          obs: A list of matching observations per agent.
          action_space: The action space for the environment using this model.
          is_communicative: Whether the action depends on communication observations as well.

        Returns a list of actions.
        """
        def act_ex_communication(agent):
            if agent.is_alive:
                action = agent.act(obs[agent.agent_id], action_space=action_space)
                if action == Action.Pause.value:
                    time.sleep(300)
                return action
            else:
                return Action.Stop.value

        def act_with_communication(agent):
            if agent.is_alive:
                action = agent.act(obs[agent.agent_id], action_space=action_space)
                if type(action) == int:
                    action = [action] + [0, 0]
                assert(type(action) == list)

                # So humans can stop the game.
                if action[0] == 6:
                    time.sleep(300)
                return action
            else:
                return [utility.Action.Stop.value, 0, 0]

        ret = []
        for agent in agents:
            if is_communicative:
                ret.append(act_with_communication(agent))
            else:
                ret.append(act_ex_communication(agent))
        return ret

    @staticmethod
    def step(actions, curr_board, curr_agents, curr_bombs, curr_items, curr_flames):
        board_size = len(curr_board)

        # Tick the flames. Replace any dead ones with passages. If there is an item there, then reveal that item.
        flames = []
        for flame in curr_flames:
            position = flame.position
            if flame.is_dead():
                item_value = curr_items.get(position)
                if item_value:
                    del curr_items[position]
                else:
                    item_value = Item.Passage.value
                curr_board[position] = item_value
            else:
                flame.tick()
                flames.append(flame)
        curr_flames = flames

        # Step the living agents.
        # If two agents try to go to the same spot, they should bounce back to their previous spots.
        # This is a little complicated because what if there are three agents all in a row.
        # If the one in the middle tries to go to the left and bounces with the one on the left,
        # and then the one on the right tried to go to the middle one's position, she should also bounce.
        # A way of doing this is to gather all the new positions before taking any actions.
        # Then, if there are disputes, correct those disputes iteratively.
        def make_counter(next_positions):
            counter = defaultdict(list)
            for num, next_position in enumerate(next_positions):
                if next_position is not None:
                    counter[next_position].append(num)
            return counter

        def has_position_conflict(counter):
            return any([len(agent_ids) > 1 for next_position, agent_ids in counter.items() if next_position])

        curr_positions = [agent.position for agent in curr_agents]
        next_positions = [agent.position for agent in curr_agents]
        for agent, action in zip(curr_agents, actions):
            if agent.is_alive:
                position = agent.position

                if action == Action.Stop.value:
                    agent.stop()
                elif action == Action.Bomb.value:
                    bomb = agent.maybe_lay_bomb()
                    if bomb:
                        curr_bombs.append(bomb)
                elif is_valid_direction(curr_board, position, action):
                    next_position = agent.get_next_position(action)

                    # This might be a bomb position. Only move in that case if the agent can kick.
                    if not position_is_bomb(curr_board, next_position):
                        next_positions[agent.agent_id] = next_position
                    elif not agent.can_kick:
                        agent.stop()
                    else:
                        next_positions[agent.agent_id] = next_position
                else:
                    # The agent made an invalid direction.
                    agent.stop()
            else:
                next_positions[agent.agent_id] = None

        counter = make_counter(next_positions)
        while has_position_conflict(counter):
            for next_position, agent_ids in counter.items():
                if next_position and len(agent_ids) > 1:
                    for agent_id in agent_ids:
                        next_positions[agent_id] = curr_positions[agent_id]
            counter = make_counter(next_positions)

        for agent, curr_position, next_position, direction in zip(curr_agents, curr_positions, next_positions, actions):
            if not agent.is_alive:
                continue

            if curr_position != next_position:
                agent.move(direction)
                if agent.can_kick:
                    bombs = [bomb for bomb in curr_bombs if bomb.position == agent.position]
                    if bombs:
                        bombs[0].moving_direction = Action(direction)

            if position_is_powerup(curr_board, agent.position):
                agent.pick_up(Item(curr_board[agent.position]))
                curr_board[agent.position] = Item.Passage.value

        # Explode bombs.
        next_bombs = []
        exploded_map = np.zeros_like(curr_board)
        for bomb in curr_bombs:
            bomb.tick()
            if bomb.is_moving():
                invalid_values = list(range(len(Item)+1))[1:]
                if is_valid_direction(curr_board, bomb.position, bomb.moving_direction.value, invalid_values=invalid_values):
                    curr_board[bomb.position] = Item.Passage.value
                    bomb.move()
                else:
                    bomb.stop()

            if bomb.exploded():
                bomb.bomber.incr_ammo()
                for _, indices in bomb.explode().items():
                    for r, c in indices:
                        if not all([r >= 0, c >= 0, r < board_size, c < board_size]):
                            break
                        if curr_board[r][c] == Item.Rigid.value:
                            break
                        exploded_map[r][c] = 1
                        if curr_board[r][c] == Item.Wood.value:
                            break
            else:
                next_bombs.append(bomb)

        # Remove bombs that were in the blast radius.
        curr_bombs = []
        for bomb in next_bombs:
            if bomb.in_range(exploded_map):
                bomb.bomber.incr_ammo()
            else:
                curr_bombs.append(bomb)

        # Kill these agents.
        for agent in curr_agents:
            if agent.in_range(exploded_map):
                agent.die()
        exploded_map = np.array(exploded_map)

        # Update the board
        for bomb in curr_bombs:
            curr_board[bomb.position] = Item.Bomb.value

        for agent in curr_agents:
            curr_board[np.where(curr_board == agent_value(agent.agent_id))] = Item.Passage.value
            if agent.is_alive:
                curr_board[agent.position] = agent_value(agent.agent_id)

        flame_positions = np.where(exploded_map == 1)
        for row, col in zip(flame_positions[0], flame_positions[1]):
            curr_flames.append(Flame((row, col)))
        for flame in curr_flames:
            curr_board[flame.position] = Item.Flames.value

        return curr_board, curr_agents, curr_bombs, curr_items, curr_flames

    def get_observations(self, curr_board, agents, bombs, is_partially_observable, agent_view_size):
        """Gets the observations as an np.array of the visible squares.

        The agent gets to choose whether it wants to keep the fogged part in memory.
        """
        board_size = len(curr_board)

        def make_bomb_map(position):
            ret = np.zeros((board_size, board_size))
            for bomb in bombs:
                x, y = bomb.position
                if not is_partially_observable or in_view_range(position, x, y):
                    ret[(x, y)] = bomb.blast_strength
            return ret

        def _in_view_range(self, position, vrow, vcol):
            row, col = position
            return all([row >= vrow - agent_view_size, row < vrow + agent_view_size,
                        col >= vcol - agent_view_size, col < vcol + agent_view_size])

        attrs = ['position', 'ammo', 'blast_strength', 'can_kick', 'teammate', 'enemies']
        keys = ['board'] + attrs

        observations = []
        for agent in agents:
            agent_obs = {}
            board = curr_board
            if is_partially_observable:
                board = board.copy()
                for row in range(board_size):
                    for col in range(board_size):
                        if not in_view_range(agent.position, row, col):
                            board[row, col] = Item.Fog.value
            agent_obs['board'] = board
            agent_obs['bombs'] = make_bomb_map(agent.position)
            for attr in attrs:
                assert hasattr(agent, attr)
                agent_obs[attr] = getattr(agent, attr)
            observations.append(agent_obs)
        return observations

    @staticmethod
    def get_done(agents, step_count, max_steps, game_type, training_agent):
        alive = [agent for agent in agents if agent.is_alive]
        alive_ids = sorted([agent.agent_id for agent in alive])
        if step_count >= max_steps:
            return True
        elif game_type == GameType.FFA:
            if training_agent is not None and training_agent not in alive_ids:
                return True
            return len(alive) <= 1
        elif any([
                len(alive_ids) <= 1,
                alive_ids == [0, 2],
                alive_ids == [1, 3],
        ]):
            return True
        return False

    @staticmethod
    def get_info(done, rewards, game_type, agents):
        if game_type == GameType.FFA:
            alive = [agent for agent in agents if agent.is_alive]
            if done and len(alive) > 1:
                return {
                    'result': Result.Tie,
                }
            elif done:
                return {
                    'result': Result.Win,
                    'winners': [num for num, reward in enumerate(rewards) if reward == 1]
                }
            else:
                return {'result': Result.Incomplete}
        elif done:
            if rewards == [1]*4:
                return {'result': Result.Tie}
            else:
                return {
                    'result': Result.Win,
                    'winners': [num for num, reward in enumerate(rewards) if reward == 1]
                }
        else:
            return {'result': Result.Incomplete}

    @staticmethod
    def get_rewards(agents, game_type, step_count, max_steps):
        alive_agents = [num for num, agent in enumerate(agents) if agent.is_alive]
        if game_type == GameType.FFA:
            ret = [-1]*4
            if len(alive_agents) == 1 or step_count >= max_steps:
                for num in alive_agents:
                    ret[num] = 1
            else:
                for num in alive_agents:
                    ret[num] = 0
            return ret
        elif alive_agents == [0, 2] or alive_agents == [0] or alive_agents == [2]:
            return [1, -1, 1, -1]
        elif alive_agents == [1, 3] or alive_agents == [1] or alive_agents == [3]:
            return [-1, 1, -1, 1]
        elif step_count >= max_steps:
            return [1]*4
        else:
            return [0]*4
