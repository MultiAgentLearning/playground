from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

from . import utility

import Box2D
from Box2D.b2 import (circleShape, fixtureDef, polygonShape,
                      revoluteJointDef, contactListener)
import numpy as np

WHEEL_R = 27
WHEEL_W = 14


def make_agents(world, num_agents_per_team,
                gas_bins=None, brake_bins=None, steer_bins=None, lidar_angles=None):
    size = 0.35
    gas_bins = gas_bins or [0, 10]
    brake_bins = brake_bins or [0, 10]
    steer_bins = steer_bins or [-5, 5]
    lidar_angles = lidar_angles or list(range(-45, 45, 5))

    agents = []
    for team in [1, 2]:
        for num_agent in range(num_agents_per_team): 
            init_x = 30 * (int(num_agent / 3) + 1)
            if team == 1:
                init_x *= -1
            init_y = 20 * (num_agent + 1)
            init_angle = np.pi if team == 1 else 0.
            agents.append(
                Agent(num_agent=num_agent, world=world,
                      gas_bins=gas_bins, brake_bins=brake_bins, steer_bins=steer_bins,
                      team=team, size=size,
                      init_angle=angle, init_x=init_x, init_y=init_y,
                      lidar_angles=lidar_angles)
            )
    return agents


class Agent():
    """Class that governs the Hockey Player object. 

    Args:
      num_agent: The indice of this agent.
      world: The Box2d world.
      gas_bins: Discrete output for the gas bins. Will be normalized to [0, 1].
      brake_bins: Discrete output for the brake bins. Will be normalized to [0, 1].
      steering_bins: Discrete output for the steering. Will be normalized to [-pi/4, pi/4]
        and applied relative to the current angle.
      team: Integer team for this agent.
      size: The float size of the agent.
      init_angle: The initial angle the agent points.
      init_x: The initial x position.
      init_y: The initial y position.
      lidar_angles: The degree angles that the lidar point with 0deg being the car front.
    """
    def __init__(self,
                 num_agent,
                 world,
                 gas_bins,
                 brake_bins,
                 steering_bins,
                 team=None,
                 size=None,
                 init_angle=None,
                 init_x=None,
                 init_y=None,
                 lidar_angles=None):
        self._size = size
        self._gas_bins = gas_bins
        self._brake_bins = brake_bins
        self._steering_bins = steering_bins
        self._max_power = 100000000 * self._size * self._size
        self._wheel_moment_of_inertia = 4000 * self._size * self._size
        self._friction_limit = 1000000 * self._size * self._size  # friction ~= mass ~= size^2 (calculated implicitly using density)
        self._num_agent = num_agent
        self._team = team
        self._lidar_angles = lidar_angles
        self._init_box2d(world, init_x, init_y, init_angle)
        self._radius = self.get_radius()

    def _init_box2d(self, world, init_x, init_y, init_angle):
        hull_poly1 = [(-60, +130), (+60, +130), (+60, +110), (-60, +110)]
        hull_poly2 = [(-15, +120), (+15, +120), (+20, +20), (-20, 20)]
        hull_poly3 = [(+25, +20), (+50, -10), (+50, -40), (+20, -90),
                      (-20, -90), (-50, -40), (-50, -10), (-25, +20)]
        hull_poly4 = [(-50, -120), (+50, -120), (+50, -90), (-50, -90)]
        hull_polies = [hull_poly1, hull_poly2, hull_poly3, hull_poly4]
        if self._team == 1:
            categoryBits = utility.TEAM1
        elif self._team == 2:
            categoryBits = utility.TEAM2

        self.body = world.CreateDynamicBody(
            position=(init_x, init_y),
            angle=init_angle,
            fixtures=[
                fixtureDef(
                    shape=polygonShape(vertices=[(x * self._size,
                                                  y * self._size)
                                                 for x, y in poly]),
                    density=1.0,
                    categoryBits=categoryBits)
                for poly in hull_polies
            ])
        self.body.num_agent = self.num_agent

        self.wheels = []
        wheel_pos = [(-55, +80), (+55, +80), (-55, -82), (+55, -82)]
        wheel_poly = [(-WHEEL_W, +WHEEL_R), (+WHEEL_W, +WHEEL_R),
                      (+WHEEL_W, -WHEEL_R), (-WHEEL_W, -WHEEL_R)]
        for wx, wy in wheel_pos:
            w = world.CreateDynamicBody(
                position=(init_x + wx * self._size, init_y + wy * self._size),
                angle=init_angle,
                fixtures=fixtureDef(
                    shape=polygonShape(vertices=[(x * self._size,
                                                  y * self._size)
                                                 for x, y in wheel_poly]),
                    density=0.1,
                    categoryBits=categoryBits,
                    # maskBits=0x001,
                    restitution=0.0))
            w.wheel_rad = WHEEL_R * self._size
            w.gas = 0.0
            w.brake = 0.0
            w.steer = 0.0
            w.phase = 0.0  # wheel angle
            w.omega = 0.0  # angular velocity
            rjd = revoluteJointDef(
                bodyA=self.body,
                bodyB=w,
                localAnchorA=(wx * self._size, wy * self._size),
                localAnchorB=(0, 0),
                enableMotor=True,
                enableLimit=True,
                maxMotorTorque=180 * 900 * self._size * self._size,
                motorSpeed=0,
                lowerAngle=-0.4,
                upperAngle=+0.4,)
            w.joint = world.CreateJoint(rjd)
            self.wheels.append(w)

    def get_radius(self):
        aabb = Box2D.b2.AABB(
            lowerBound=Box2D.Box2D.b2Vec2(10000, 10000),
            upperBound=Box2D.Box2D.b2Vec2(-10000, -10000))
        for fixture in self.body.fixtures:
            aabb.Combine(aabb, fixture.GetAABB(0))
        return utility.get_distance(aabb.upperBound, aabb.center)

    def gas(self, gas):
        """Apply gas.

        We cap the absolute difference between the normalized gas and the previous gas to be .25.

        Args:
          gas: An integer bin to accelerate towards.
        """
        gas = 1. * gas / (self._gas_bins[1] - self._gas_bins[0])
        for w in self.wheels[2:4]:
            wgas = max(gas, w.gas - .25)
            wgas = min(wgas, w.gas + .25)
            w.gas += wgas - w.gas

    def brake(self, brake):
        """How much to brake."""
        brake = 1. * brake / (self._brake_bins[1] - self._brake_bins[0])
        for w in self.wheels:
            w.brake = brake

    def steer(self, angle):
        """Apply steering. We cap this to be in [-pi/4, pi/4]."""
        x, y = self._steering_bin-range
        normalizing_p = np.pi/(2. * (y - x))
        normalizing_q = -np.pi * (y + x) / (4. * (y - x))
        radians = normalizing_p * angle + normalizing_q
        for w in self.wheels[:2]:
            w.steer += radians

    def set_lidar_observations(self, world):
        lidar_range = 300 # Covers the full diagonal of the rink.
        px, py = self.get_position()
        hull_angle = self.get_hull_angle()
        radians = np.asarray([angle * np.pi / 180. + hull_angle for angle in self.lidar_angles])
        p1 = np.stack([
            px + self.radius * np.cos(radians),
            py + self.radius * np.sin(radians)
        ]).transpose()
        p2 = np.stack([
            px + lidar_range * np.cos(radians),
            py + lidar_range * np.sin(radians)
        ]).transpose()
        collision_categories = [0 for _ in range(p1.shape[0])]

        for i in range(p1.shape[0]):
            lidar_callback.p1 = (p1[i, 0], p1[i, 1])
            lidar_callback.p2 = (p2[i, 0], p2[i, 1])
            world.RayCast(lidar_callback, lidar_callback.p1, lidar_callback.p2)
            p1[i, :2] = lidar_callback.p1[:2]
            p2[i, :2] = lidar_callback.p2[:2]
            collision_categories[i] = lidar_callback.category
        lidar_distances = np.linalg.norm(p1 - p2, ord=2, axis=1).tolist()

        self.lidar_points = [((p1[i, 0], p1[i, 1]), (p2[i, 0], p2[i, 1])) for i in range(p1.shape[0])]
        self.lidar_observations = lidar_distances + collision_categories

    def set_personal_observations(self, world, score, time_remaining):
        team = self._team
        x, y = self.get_position()
        vx, vy = self.get_linear_velocity()
        wheel_angle = self.get_wheel_angle()
        hull_angle = self.get_hull_angle()
        self.personal_observations = [team, x, y, vx, vy, wheel_angle, hull_angle, time_remaining] + score

    def step(self, dt):
        for w in self.wheels:
            # Steer each wheel
            dir = np.sign(w.steer - w.joint.angle)
            val = abs(w.steer - w.joint.angle)
            w.joint.motorSpeed = dir * min(50.0 * val, 3.0)

            # Force
            forw = w.GetWorldVector((0, 1))
            side = w.GetWorldVector((1, 0))
            v = w.linearVelocity
            vf = forw[0] * v[0] + forw[1] * v[1]  # forward speed
            vs = side[0] * v[0] + side[1] * v[1]  # side speed

            w.omega += dt * self._max_power * w.gas / (self._wheel_moment_of_inertia * (abs(w.omega) + 5.0))
            if w.brake >= 0.9:
                w.omega = 0
            elif w.brake > 0:
                brake_force = 15  # radians per second
                dir = -np.sign(w.omega)
                val = brake_force * w.brake
                if abs(val) > abs(w.omega):
                    val = abs(w.omega)  
                w.omega += dir * val
            w.phase += w.omega * dt

            vr = w.omega * w.wheel_rad  # rotating wheel speed
            f_force = -vf + vr  # direction is direction of speed difference
            p_force = -vs

            # Physically correct is to always apply friction_limit until speed is equal.
            # But dt is finite, that will lead to oscillations if difference is already near zero.
            f_force *= 205000 * self._size * self._size  
            p_force *= 205000 * self._size * self._size
            force = np.sqrt(np.square(f_force) + np.square(p_force))

            if abs(force) > self._friction_limit:
                f_force /= force
                p_force /= force
                force = self._friction_limit
                f_force *= force
                p_force *= force

            w.omega -= dt * f_force * w.wheel_rad / self._wheel_moment_of_inertia

            w.ApplyForceToCenter((p_force * side[0] + f_force * forw[0],
                                  p_force * side[1] + f_force * forw[1]),
                                 True)

    def render(self):
        hull = None
        wheels = []

        hull_path = []
        angle = self.get_hull_angle() 
        position = self.get_position()[:2]

        for obj in self.wheels + [self.hull]:
            for f in obj.fixtures:
                trans = f.body.transform
                if "phase" not in obj.__dict__:
                    path = [trans * v for v in f.shape.vertices]
                    path = [(v[0], v[1]) for v in path]  # for serializing
                    hull_path.append(path)
                    continue

                a1 = obj.phase - np.pi / 2.0
                a2 = a1 - 1.2
                s1 = math.sin(a1)
                s2 = math.sin(a2)
                c1 = math.cos(a1)
                c2 = math.cos(a2)
                if s1 > 0 and s2 > 0:
                    continue
                if s1 > 0:
                    c1 = np.sign(c1)
                if s2 > 0:
                    c2 = np.sign(c2)
                white_poly = [(-WHEEL_W * self._size,
                               +WHEEL_R * c1 * self._size),
                              (+WHEEL_W * self._size,
                               +WHEEL_R * c1 * self._size),
                              (+WHEEL_W * self._size,
                               +WHEEL_R * c2 * self._size),
                              (-WHEEL_W * self._size,
                               +WHEEL_R * c2 * self._size)]
                path = [trans * v for v in white_poly]
                path = [(v[0], v[1]) for v in path]
                wheels.append({
                    "path": path,
                    "angles": (a1 * 180.0 / np.pi, a2 * 180.0 / np.pi)
                })

        hull = {"path": hull_path, "position": position, "angle": angle}
        velocity = self.get_linear_velocity()
        current_speed = np.linalg.norm(velocity)

        return {
            "lidar": self.lidar_observations,
            "wheels": wheels,
            "hull": hull,
            "goal": self.goal.num_goal,
            "currspeed": '%.3f' % current_speed,
            "num_agent": self._num_agent,
            "team": self._team,
        }

    def get_true_speed(self):
        return np.linalg.norm(self.get_linear_velocity())

    def get_position(self):
        return self.body.position

    def get_wheel_angle(self):
        return self.wheels[0].joint.angle % (2*np.pi)

    def get_hull_angle(self):
        return self.body.angle % (2*np.pi)

    def get_linear_velocity(self):
        return self.body.linearVelocity

    def destroy(self, world):
        for wheel in self.wheels:
            world.DestroyJoint(wheel.joint)
            for fixture in wheel.fixtures:
                wheel.DestroyFixture(fixture)
            world.DestroyBody(wheel)

        for fixture in self.body.fixtures:
            self.body.DestroyFixture(fixture)
        world.DestroyBody(self.body)


class LidarCallback(Box2D.b2.rayCastCallback):
    """Box2d Lidar Class."""

    def ReportFixture(self, fixture, point, normal, fraction):
        if fixture.filterData.categoryBits == utility.SKIP:
            return -1

        self.category = utility.CATEGORY_BITS.index(fixture.filterData.categoryBits)
        self.p2 = point
        self.fraction = fraction
        return fraction
lidar_callback = LidarCallback()
