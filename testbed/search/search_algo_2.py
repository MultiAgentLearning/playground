import queue

"""
Constants that you will need to infer the state of the board.
"""
PASSAGE = 0  # any plain cell that a player can pass through
RIGID_WALL = 1  # a wall that cannot be passed through or bombed
PLAYER = 10  # the player agent
GOAL_ITEM = 8  # the goal item that will mark the end of the game

"""
Actions that you will need to include in your returned list object.
"""
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4


# driver function that will be called by runner script
def search(board, agent_position):
    """
    Compute the sequence of actions required for agent to move to the cell containing a goal item.

    Args:
        board:
            - A 2-Dimensional Square Matrix (i.e. width = height)
            - Can have a variable width so ensure your program adapts to different square board sizes
            - The board contains integer values which represent objects that are positioned on that cell.
            For example, if board[y][x] = 2, there is a wooden wall at coordinates (x, y) of the board, i.e.
            the (x + 1)th column and the (y + 1)th row of the board. DO REMEMBER WE ARE USING 0-BASED INDEXING.
            - Refer to constants defined at the top of this file to understand the different object representations.

        agent_position:
            - A 2-tuple (y, x) that corresponds to initial position of agent on the board that corresponds to the (y + 1)th
            row and the (x + 1)th column of the board.

    Returns:
        actions: A list of valid integer actions. Do refer to the definition of valid actions near the top of the file.
    """

    goal_position = find_goal_position(board)

    return breadth_first_search(board, agent_position, goal_position)


# performs breadth first search
def breadth_first_search(board, initial_position, goal_position):
    if (is_goal(initial_position, goal_position)):
        return []

    # define every node to be a tuple with the following structure: (path cost, (position, actions taken))
    frontier = queue.Queue()
    frontier_coordinates = set()
    expanded = set()

    frontier.put((0, (initial_position, [])))
    frontier_coordinates.add(initial_position)

    while not frontier.empty():
        node = frontier.get()
        node_position = node[1][0]
        frontier_coordinates.remove(node_position)
        node_path = node[1][1]
        node_path_cost = node[0]  # every action has uniform cost

        expanded.add(node_position)

        children = generate_valid_children_positions(node_position, board)

        for action_to_get_child in list(children.keys()):
            action = action_to_get_child
            new_path = node_path.copy()
            new_path.append(action)
            child_position = children.get(action)
            child_path_cost = node_path_cost + 1
            child_node = (child_path_cost,
                          (child_position, new_path))

            if (is_goal(child_position, goal_position)):
                return new_path

            if (child_position not in frontier_coordinates and child_position not in expanded):
                frontier_coordinates.add(child_position)
                frontier.put(child_node)


# generates valid successor nodes of current position
def generate_valid_children_positions(position, board):
    children_positions = dict()
    curr_row = position[0]
    curr_col = position[1]

    # Consider Up
    if (curr_row > 0 and board[curr_row - 1, curr_col] != RIGID_WALL):
        children_positions[UP] = (curr_row - 1, curr_col)
    # Consider Down
    if (curr_row < len(board) - 1 and board[curr_row + 1, curr_col] != RIGID_WALL):
        children_positions[DOWN] = (curr_row + 1, curr_col)
    # Consider Left
    if (curr_col > 0 and board[curr_row, curr_col - 1] != RIGID_WALL):
        children_positions[LEFT] = (curr_row, curr_col - 1)
    # Consider Right
    if (curr_col < len(board[0]) - 1 and board[curr_row, curr_col + 1] != RIGID_WALL):
        children_positions[RIGHT] = (curr_row, curr_col + 1)

    return children_positions


# determines if a position is a goal position
def is_goal(position, goal_position):
    return position == goal_position


# finds goal position from board matrix
def find_goal_position(board):
    for y in range(len(board)):
        for x in range(len(board[0])):
            if(board[y][x] == GOAL_ITEM):
                return (y, x)
