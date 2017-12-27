from enum import Enum

# These are categoryBits used in the fixtures.
SKIP = 0x0010
GOAL1 = 0x0020
GOAL2 = 0x0030
PUCK = 0x0040
WALL = 0x0050
TEAM1 = 0x0060
TEAM2 = 0x0070
CATEGORY_BITS = [SKIP, GOAL1, GOAL2, PUCK, WALL, TEAM1, TEAM2]


def get_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2 - y1)**2 + (x2 - x1)**2)


def flatten(lst):
    return [item for sublist in lst for item in sublist]
