import copy
import math
import numpy as np

from . import utility
from . import constants


class MCTNode:
    def __init__(self, game_env, agent_id, agent_memory):
        self.game_env = game_env
        self.agent_id = agent_id    # The playing agent
        self.agent_memory = agent_memory
        self.parent_edge = None
        self.child_edges = []


    def is_leaf(self):
        return len(self.child_edges) == 0

    def get_agent_obj(self):
        for agent in self.game_env._agents:
            if agent.agent_id == self.agent_id:
                return agent
        raise ValueError('Invalid agent id was stored in this node!')

    def get_agent_laid_bombs(self):
        return [b for b in self.game_env._bombs if b.bomber.agent_id == self.agent_id]

    def get_alive_agents(self):
        return [agent.agent_id for agent in self.game_env._agents if agent.is_alive]


class MCTEdge:
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

        self.visit_count = 0
        self.total_reward = 0
        self.avg_reward = 0


def selection_policy(node, c_uct):
    """ 
    Given a tree node, determine which 
    child to move to when performing MCTS;
    c_uct: constant for UCT algorithm
    """

    if node.is_leaf():
        return node

    max_child = None
    max_val = float('-inf')
    total_visit = 1

    for edge in node.child_edges:
        total_visit += edge.visit_count

    # Determine best child to move to according to UCT
    for edge in node.child_edges:
        if edge.visit_count == 0:
            edge_val = 0
        else:
            edge_val = edge.total_reward / edge.visit_count
        edge_val += c_uct * math.sqrt(2 * math.log(total_visit) / (1 + edge.visit_count))

        if edge_val > max_val:
            max_val = edge_val
            max_child = edge.child

    return max_child


def select(root):
    """
    Selection stage of MCTS: move to leaf for expanding the search tree
    :param root: MCTNode, root of the tree
    :return: MCTNode, a leaf
    """
    cur = root
    while not cur.is_leaf():
        cur = selection_policy(cur, constants.UCT_C)
    return cur


def decide_reward(prev_node, cur_node):
    """
    Given the current state of game and its previous state as MCTNode,
    decide what reward is to be given to the current agent for this state transition
    :param prev_node: Previous game state as MCTNode
    :param next_node: Current game state as MCTNode
    :return: reward from state transition, as integer
    """
    # Constant decay
    reward = constants.REWARD_DECAY

    # First check if any players died
    prev_agent_ids = prev_node.get_alive_agents()
    cur_agent_ids = cur_node.get_alive_agents()
    missing_agent_ids = [agent for agent in prev_agent_ids if agent not in cur_agent_ids]
    this_agent = cur_node.get_agent_obj()

    # Agent died
    if this_agent.agent_id in missing_agent_ids:
        reward += constants.REWARD_DIED

    # Check if any enemies died (regardless of dying from whom)
    for enemy in this_agent.enemies:
        enemy_agent_id = int(enemy.name[-1])
        if enemy_agent_id in missing_agent_ids:
            reward += constants.REWARD_ENEMY_DIED


    # Then, check if picked up powerups
    cur_pos = this_agent.position
    item_enum = constants.Item
    powerups = [item_enum.Kick, item_enum.IncrRange, item_enum.ExtraBomb]

    if prev_node.game_env._board[cur_pos] in [p.value for p in powerups]:
        reward += constants.REWARD_POWERUP


    # Lastly, check if agent destroyed any wood boxes
    prev_laid_bombs = prev_node.get_agent_laid_bombs()

    def reward_bomb_for_direction(bomb, prev_board, cur_board, direction):
        for off in range(1, bomb.blast_strength):
            pos = (bomb.position[0] + off * direction[0], bomb.position[1] + off * direction[1])
            exit = False
            # If the explosion is blocked, exit early
            if not utility.position_on_board(prev_board, pos) or utility.position_is_wall(prev_board, pos):
                exit = True
            # If a wood box is to be flamed in previous state and
            # is actually flamed in current state, then give reward
            if utility.position_is_wood(prev_board, pos) and utility.position_is_flames(cur_board, pos):
                return constants.REWARD_WOOD
            if exit:
                break
        return 0


    for bomb in prev_laid_bombs:
        # About to explode
        if bomb.life == 1:
            # NOTE:
            #   For now, as long as any wood boxes are destroyed within the bomb range
            #   of this exploding bomb it's counted towards this agent.
            #   If bomb life > 1 but it's triggered by other bombs then we don't care
            prev_board, cur_board = prev_node.game_env._board, cur_node.game_env._board
            reward += reward_bomb_for_direction(bomb, prev_board, cur_board, direction=(1, 0))
            reward += reward_bomb_for_direction(bomb, prev_board, cur_board, direction=(0, 1))
            reward += reward_bomb_for_direction(bomb, prev_board, cur_board, direction=(-1, 0))
            reward += reward_bomb_for_direction(bomb, prev_board, cur_board, direction=(0, -1))

    return reward


def rollout_policy(node):
    """
    Given a tree node, determine what actions to take
    when rolling out
    :param node: The input MCTNode
    :return: The actions of all 4 agents for transitioning to next state
    """
    # NOTE: Use Simple Agent for now
    agents_obs = node.game_env.get_observations()
    agents_obs[node.agent_id] = utility.combine_agent_obs_and_memory(node.agent_memory, agents_obs[node.agent_id])
    actions = node.game_env.act(agents_obs)
    return actions


def rollout(leaf, depth):
    """
    Given current node, rollout to the given depth following the rollout policy
    and accumulate all immediate reward back to the starting node
    :param leaf: MCTNode as leaf
    :param depth: The number of times to simulate for collecting immediate rewards
    :return: Total reward collected by rolling out from the input leaf
    """
    if depth <= 0:
        return 0

    total_reward = 0
    prev_state = leaf

    for i in range(depth):
        cur_state = copy.deepcopy(prev_state)
        agent_actions = rollout_policy(cur_state)
        agents_obs, _, done, _ = cur_state.game_env.step(agent_actions)

        # After making a move, update the memory kept on this node
        cur_state.agent_memory = utility.update_agent_memory(cur_state.agent_memory,
                                                             agents_obs[cur_state.agent_id])

        reward = decide_reward(prev_state, cur_state)
        total_reward += reward

        if done:
            break

    return total_reward


def expand(node):
    """
    Expansion stage of MCTS
        - create child nodes at the given leaf
        - updates MCTEdge statistics for the given leaf

    :param node: the leaf node to expand
    :return: None
    """
    if not node.is_leaf():
        return

    # build children
    is_done = []
    for action in constants.Action:
        child_node = copy.deepcopy(node)
        agents_obs = node.game_env.get_observations()

        # Combine current observation with the agent's memory of the game
        agents_obs[node.agent_id] = utility.combine_agent_obs_and_memory(node.agent_memory, agents_obs[node.agent_id])

        # Replace the current agent's action with the action we are searching
        agents_actions = node.game_env.act(agents_obs)
        agents_actions[node.agent_id] = action.value

        # Apply actions to environment, while checking if reaching a terminal state
        new_agents_obs, _, done, _ = child_node.game_env.step(agents_actions)
        is_done.append(done)

        # Update agent's memory after stepping
        child_node.agent_memory = utility.update_agent_memory(child_node.agent_memory,new_agents_obs[child_node.agent_id])

        # Build Tree
        new_edge = MCTEdge(node, child_node)
        child_node.parent_edge = new_edge
        node.child_edges.append(new_edge)

    # rollout for each children, and then send the average reward back to root via the current leaf
    leaf_avg_reward = 0

    for done, edge in zip(is_done, node.child_edges):
        child_node = edge.child
        if done:
            leaf_avg_reward += decide_reward(prev_node=node, cur_node=child_node)
        else:
            leaf_avg_reward += rollout(child_node, constants.ROLLOUT_DEPTH)

    leaf_avg_reward /= len(node.child_edges)

    # Backup the value to root
    backup(node.parent_edge, leaf_avg_reward)


def backup(from_edge, reward):
    """
    Given the lowest edge in the search tree, backup its
    value along all edges to the root
    :param from_edge: the edge
    :return: None
    """
    cur_edge = from_edge

    while cur_edge is not None and cur_edge.parent is not None:
        cur_edge.total_reward += reward
        cur_edge.visit_count += 1
        cur_edge.avg_reward = cur_edge.total_reward / cur_edge.visit_count
        cur_edge = cur_edge.parent.parent_edge


def perform_MCTS(game_env, agent_id, agent_memory):
    # Copy the game env so the original is not affected
    root = MCTNode(copy.deepcopy(game_env), agent_id, agent_memory)

    for i in range(constants.NUM_SIMULATIONS):
        leaf = select(root)
        expand(leaf)

    next_rewards = [edge.avg_reward for edge in root.child_edges]
    pi = utility.softmax(next_rewards)
    return pi

