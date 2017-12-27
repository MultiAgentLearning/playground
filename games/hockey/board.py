from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Box2D.b2 import (edgeShape, fixtureDef)
import numpy as np

from . import utility


def make_game(world):
    """Build the Box2D game setting."""
    rink_width = 200
    rink_height = 85
    rink_radius = 28
    rink_radius_num = 15
    return Rink(world, rink_width, rink_height, rink_radius, rink_radius_num)


class Rink():
    """Class that governs the Rink object, which is the "board" on which the players play.

    The rink is NHL dimensions, 200ft by 85ft with a 28ft radius. The goal line is 11ft from the end,
    the goal depth is 3 1/3 ft, and the width is 6ft. Because drawing an arc in Box2D is hard, we use
    an inscribed polygon.
    """

    def __init__(self, world, rink_width=200, rink_height=85, rink_radius=28, rink_radius_num=12,
                 puck_radius=3, goal_line=11, goal_depth=3.5, goal_width=6):
        self.world = world
        self._make_body(rink_width, rink_height, rink_radius, rink_radius_num)
        self._make_puck(puck_radius, 0, 0)
        self._make_goals(rink_width, rink_height, goal_line, goal_depth, goal_width)

    def _make_body(self, rink_width, rink_height, rink_radius, rink_radius_num):
        x_translation = -rink_width/2
        y_translation = -rink_height/2
        curve_radians = np.pi / (4 * rink_radius_num)

        fixture_vertices = [
            (0, rink_radius),
        ]
        for curve_num in range(1, rink_radius_num+1):
            radians = curve_num * curve_radians
            x, y = (0, rink_radius)
            c = rink_radius * np.sqrt(2 * (1 - np.cos(curve_radians)))
            y -= c * cos(curve_radians)
            x += c * sin(curve_radians)
            fixture_vertices.append((x, y))

        fixture_vertices.append(
            (rink_width - rink_radius, 0)
        )
        for curve_num in range(1, rink_radius_num+1):
            radians = curve_num * curve_radians
            x, y = (rink_width - rink_radius, 0)
            c = rink_radius * np.sqrt(2 * (1 - np.cos(curve_radians)))
            y += c * sin(curve_radians)
            x += c * cos(curve_radians)
            fixture_vertices.append((x, y))

        fixture_vertices.append(
            (rink_width, rink_height - rink_radius)
        )
        for curve_num in range(1, rink_radius_num+1):
            radians = curve_num * curve_radians
            x, y = (rink_width, rink_height - rink_radius)
            c = rink_radius * np.sqrt(2 * (1 - np.cos(curve_radians)))
            y += c * cos(curve_radians)
            x -= c * sin(curve_radians)
            fixture_vertices.append((x, y))

        fixture_vertices.append(
            (rink_radius, rink_height)
        )
        for curve_num in range(1, rink_radius_num+1):
            radians = curve_num * curve_radians
            x, y = (rink_radius, rink_height)
            c = rink_radius * np.sqrt(2 * (1 - np.cos(curve_radians)))
            y -= c * sin(curve_radians)
            x -= c * cos(curve_radians)
            fixture_vertices.append((x, y))

        fixture_vertices.append([
            (0, rink_radius),
        ])

        self.body = self.world.CreateStaticBody(fixtures=[
            fixtureDef(
                shape=edgeShape(vertices=[(x + x_translation, y + y_translation) for x, y in fixture_vertices]),
                categoryBits=utility.WALL
            )
        ])

    def _make_puck(self, radius, init_x, init_y):
        self.puck = Puck(self.world, init_x, init_y, radius)

    def _make_goals(self, rink_width, rink_height, goal_line, goal_depth, goal_width):
        x_translation = -rink_width/2
        y_translation = -rink_height/2
        self.goals = [
            Goal(self.world, rink_width, rink_height, goal_line, goal_depth, goal_width,
                 x_translation=x_translation, y_translation=y_translation, team=i+1)
            for i in range(2)
        ]

    def _render(self):
        rink = self._render_rink()
        puck = self._render_puck()
        goals = self._render_goals()
        return {"rink": rink, "puck": puck, "goals": goals}

    def _render_rink(self):
        return {'vertices': utility.flatten([fixture.shape.vertices for fixture in self.body.fixtures])}

    def _render_puck(self):
        return self.puck.render()

    def _render_goals(self):
        return [goal.render() for goal in self.goals]

    def destroy(self, world):
        world.DestroyBody(self.body)
        self.puck.destroy(world)
        for goal in self.goals:
            goal.destroy(world)


class Puck(object):
    """Class governing the puck object."""

    def __init__(self,
                 world,
                 init_x=None,
                 init_y=None,
                 radius=3.0):
        self.radius = radius
        self.body = world.CreateDynamicBody(
            position=(init_x, init_y),
            fixtures=[
                fixtureDef(
                    shape=circleShape(radius=self.radius),
                    categoryBits=utility.PUCK)
            ]
        )
        self.body.is_puck = True

    def get_position(self):
        return self.body.position

    def render(self):
        position = self.get_position()
        position = (position[0], position[1])
        return {
            'position': position,
            'radius': self.radius,
        }

    def destroy(self, world):
        world.DestroyBody(self.body)


class Goal(object):
    """Class governing the goal object.

    A goal is defined by two open polygons, one inside the other. The outer one is what the Lidar sees.
    The inner one is used to define if there has been a goal. The reason that we differentiate these is
    so that we don't run into issues where contact begins with an outer edge.
    """
    def __init__(self,
                 world,
                 rink_width,
                 rink_height,
                 goal_line,
                 goal_depth,
                 goal_width,
                 x_translation=0,
                 y_translation=0,
                 team=None):
        assert team == 1 or team == 2
        self.team = team

        outer_vertices = []
        inner_vertices = []
        padding = 0.5
        if team == 1:
            outer_vertices.append((goal_line, rink_height/2 + goal_width/2))
            outer_vertices.append((goal_line - goal_depth, rink_height/2 + goal_width/2))
            outer_vertices.append((goal_line - goal_depth, rink_height/2 - goal_width/2))
            outer_vertices.append((goal_line, rink_height/2 - goal_width/2))
            inner_vertices.append((goal_line - padding, rink_height/2 + goal_width/2 - padding))
            inner_vertices.append((goal_line - goal_depth + padding, rink_height/2 + goal_width/2 - padding))
            inner_vertices.append((goal_line - goal_depth + padding, rink_height/2 - goal_width/2 + padding))
            inner_vertices.append((goal_line - padding, rink_height/2 - goal_width/2 + padding))
        else:
            outer_vertices.append((rink_width - goal_line, rink_height/2 - goal_width/2))
            outer_vertices.append((rink_width - goal_line + goal_depth, rink_height/2 - goal_width/2))
            outer_vertices.append((rink_width - goal_line + goal_depth, rink_height/2 + goal_width/2))
            outer_vertices.append((rink_width - goal_line, rink_height/2 + goal_width/2))
            inner_vertices.append((rink_width - goal_line - padding, rink_height/2 - goal_width/2 + padding))
            inner_vertices.append((rink_width - goal_line + goal_depth + padding, rink_height/2 - goal_width/2 + padding))
            inner_vertices.append((rink_width - goal_line + goal_depth + padding, rink_height/2 + goal_width/2 - padding))
            inner_vertices.append((rink_width - goal_line - padding, rink_height/2 + goal_width/2 - padding))

        categoryBits = utility.GOAL1 if self.team == 1 else utility.GOAL2
        self.outer = world.CreateStaticBody(fixtures=[
            fixtureDef(
                shape=edgeShape(vertices=[(x + x_translation, y + y_translation) for x, y in outer_vertices]),
                categoryBits=categoryBits
            )
        ])
        self.inner = world.CreateStaticBody(fixtures=[
            fixtureDef(
                shape=edgeShape(vertices=[(x + x_translation, y + y_translation) for x, y in inner_vertices]),
                categoryBits=utility.SKIP
            )
        ])
        self.inner.is_goal = True
        self.inner.team = self.team

    def render(self):
        return {
            'outer_vertices': utility.flatten([fixture.shape.vertices for fixture in self.outer.fixtures]),
            'inner_vertices': utility.flatten([fixture.shape.vertices for fixture in self.inner.fixtures])
        }

    def destroy(self, world):
        world.DestroyBody(self.body)


class GoalListener(contactListener):
    """Listener for goals."""

    def __init__(self, env):
        contactListener.__init__(self)
        self.env = env

    def BeginContact(self, contact):
        self._contact(contact, True)

    def EndContact(self, contact):
        self._contact(contact, False)

    def _contact(self, contact, begin):
        """TODO: Get this to work properly."""
        def get_objects(a, b):
            if hasattr(a, 'is_goal'):
                team = a.team
                if hasattr(b, 'is_puck'):
                    return team, True
            return None, False

        u1 = contact.fixtureA.body
        u2 = contact.fixtureB.body

        team, is_success = get_objects(u1, u2)
        if not is_success:
            team, is_success = get_objects(u2, u1)
        if not is_success:
            return

        # Team is the side on which the goal was scored. This means that the other side gets the point.
        self.env._score_on_goal = team
