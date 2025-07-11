import random
import math
import numpy as np

import pymunk


PI = math.pi


def random_body_position(body):
    ''' pick a random point along the boundary'''
    width, length = body.dimensions
    if random.randint(0, 1) == 0:
        # force along ends
        if random.randint(0, 1) == 0:
            # force on the left end
            location = (random.uniform(0, width), 0)
        else:
            # force on the right end
            location = (random.uniform(0, width), length)
    else:
        # force along length
        if random.randint(0, 1) == 0:
            # force on the bottom end
            location = (0, random.uniform(0, length))
        else:
            # force on the top end
            location = (width, random.uniform(0, length))
    return location

def random_direction(velocity):
    angle = random.uniform(0, 2*PI)
    return (velocity * math.cos(angle), velocity * math.sin(angle))


class PymunkMultibody(object):
    """
    Multibody object for interfacing with pymunk
    """

    defaults = {
        'agent_shape': 'circle',
        # hardcoded parameters
        'elasticity': 0.9,
        'damping': 0.5,  # 1 is no damping, 0 is full damping
        'angular_damping': 0.8,
        'friction': 0.9,  # does this do anything?
        'physics_dt': 0.001,
        'force_scaling': 5e4,  # scales from pN
        # configured parameters
        'jitter_force': 1e-3,  # pN
        'bounds': [20, 20],
        'barriers': False,
        'initial_agents': {},
    }

    def __init__(self, config):
        # hardcoded parameters
        self.elasticity = self.defaults['elasticity']
        self.friction = self.defaults['friction']
        self.damping = self.defaults['damping']
        self.angular_damping = self.defaults['angular_damping']
        self.physics_dt = config.get('physics_dt', self.defaults['physics_dt'])
        self.force_scaling = self.defaults['force_scaling']

        # configured parameters
        self.agent_shape = config.get('agent_shape', self.defaults['agent_shape'])
        self.jitter_force = config.get('jitter_force', self.defaults['jitter_force'])
        self.bounds = config.get('bounds', self.defaults['bounds'])
        barriers = config.get('barriers', self.defaults['barriers'])

        # initialize pymunk space
        self.space = pymunk.Space()

        # add static barriers
        self.add_barriers(self.bounds, barriers)

        # initialize agents
        initial_agents = config.get('initial_agents', self.defaults['initial_agents'])
        self.bodies = {}
        for agent_id, specs in initial_agents.items():
            self.add_body_from_center(agent_id, specs)

    def run(self, timestep):
        if self.physics_dt > timestep:
            print('timestep skipped by pymunk_multibody: {}'.format(timestep))
            return

        time = 0
        while time < timestep:
            time += self.physics_dt

            # apply forces
            # for body in self.space.bodies:
            #     self.apply_jitter_force(body)
            #     self.apply_viscous_force(body)

            # run for a physics timestep
            self.space.step(self.physics_dt)

    def apply_jitter_force(self, body):
        jitter_location = random_body_position(body)
        jitter_force = [
            random.normalvariate(0, self.jitter_force),
            random.normalvariate(0, self.jitter_force)]
        scaled_jitter_force = [
            force * self.force_scaling
            for force in jitter_force]
        body.apply_impulse_at_local_point(
            scaled_jitter_force,
            jitter_location)

    def apply_viscous_force(self, body):
        # dampen velocity
        body.velocity = body.velocity * self.damping + (body.force / body.mass) * self.physics_dt

        # dampen angular velocity
        body.angular_velocity = body.angular_velocity * self.angular_damping + (body.torque / body.moment) * self.physics_dt

    def add_barriers(self, bounds, barriers):
        """ Create static barriers """
        thickness = 50.0
        offset = thickness
        x_bound = bounds[0]
        y_bound = bounds[1]

        static_body = self.space.static_body
        static_lines = [
            pymunk.Segment(
                static_body,
                (0.0-offset, 0.0-offset),
                (x_bound+offset, 0.0-offset),
                thickness),
            pymunk.Segment(
                static_body,
                (x_bound+offset, 0.0-offset),
                (x_bound+offset, y_bound+offset),
                thickness),
            pymunk.Segment(
                static_body,
                (x_bound+offset, y_bound+offset),
                (0.0-offset, y_bound+offset),
                thickness),
            pymunk.Segment(
                static_body,
                (0.0-offset, y_bound+offset),
                (0.0-offset, 0.0-offset),
                thickness),
        ]

        if barriers:
            spacer_thickness = barriers.get('spacer_thickness', 0.1)
            channel_height = barriers.get('channel_height')
            channel_space = barriers.get('channel_space')
            n_lines = math.floor(x_bound/channel_space)

            machine_lines = [
                pymunk.Segment(
                    static_body,
                    (channel_space * line, 0),
                    (channel_space * line, channel_height), spacer_thickness)
                for line in range(n_lines)]
            static_lines += machine_lines

        for line in static_lines:
            line.elasticity = 0.0  # bounce
            line.friction = 0.8
            self.space.add(line)

    def get_shape(self, boundary):
        '''
        shape documentation at: https://pymunk-tutorial.readthedocs.io/en/latest/shape/shape.html
        '''

        if self.agent_shape == 'segment':
            width = boundary['width']
            length = boundary['length']

            half_width = width / 2
            half_length = length / 2 - half_width
            shape = pymunk.Segment(
                None,
                (-half_length, 0),
                (half_length, 0),
                radius=half_width)

        elif self.agent_shape == 'circle':
            diameter = boundary['diameter']
            radius = diameter / 2
            shape = pymunk.Circle(None, radius=radius, offset=(0, 0))

        elif self.agent_shape == 'rectangle':
            width = boundary['width']
            length = boundary['length']
            half_length = length / 2
            half_width = width / 2
            shape = pymunk.Poly(None,
                ((-half_length, -half_width),
                 (half_length, -half_width),
                 (half_length, half_width),
                 (-half_length, half_width)))

        return shape

    def get_inertia(self, shape, mass):
        if self.agent_shape == 'rectangle':
            inertia = pymunk.moment_for_poly(mass, shape.get_vertices())
        elif self.agent_shape == 'circle':
            radius = shape.radius
            inertia = pymunk.moment_for_circle(mass, radius, radius)
        elif self.agent_shape == 'segment':
            a = shape.a
            b = shape.b
            radius = shape.radius
            inertia = pymunk.moment_for_segment(mass, a, b, radius)

        return inertia

    def add_body_from_center(self, body_id, specs):
        boundary = specs['boundary']
        mass = boundary['mass']
        center_position = boundary['location']
        angular_velocity = boundary.get('angular_velocity', 0.0)

        if self.agent_shape == 'circle':
            boundary = specs['boundary']
            mass = boundary['mass']
            center_position = boundary['location']
            diameter = boundary['diameter']

            # get shape, inertia, make body, assign body to shape
            shape = self.get_shape(boundary)
            inertia = self.get_inertia(shape, mass)
            body = pymunk.Body(mass, inertia)
            shape.body = body

            body.position = (
                center_position[0],
                center_position[1])
            body.diameter = diameter

        elif self.agent_shape == 'segment':
            angle = boundary['angle']
            width = boundary['width']
            length = boundary['length']

            # get shape, inertia, make body, assign body to shape
            shape = self.get_shape(boundary)
            inertia = self.get_inertia(shape, mass)
            body = pymunk.Body(mass, inertia)
            shape.body = body

            body.position = (
                center_position[0],
                center_position[1])
            body.angle = angle
            body.dimensions = (width, length)
            body.angular_velocity = angular_velocity

        else:
            raise ValueError('agent_shape needs to be segment or circle')

        shape.elasticity = self.elasticity
        shape.friction = self.friction

        # add body and shape to space
        self.space.add(body, shape)

        # add body to agents dictionary
        self.bodies[body_id] = (body, shape)

    def set_velocity(self, body_id, velocity):
        body, shape = self.bodies[body_id]
        body.velocity = random_direction(velocity)

    def update_body(self, body_id, specs):
        boundary = specs['boundary']
        if self.agent_shape == 'circle':

            diameter = boundary['diameter']
            mass = boundary['mass']
            velocity = boundary['velocity']

            body, shape = self.bodies[body_id]
            position = body.position

            # get shape, inertia, make body, assign body to shape
            new_shape = self.get_shape(boundary)
            inertia = self.get_inertia(new_shape, mass)
            new_body = pymunk.Body(mass, inertia)
            new_shape.body = new_body

            new_body.position = position
            new_body.velocity = body.velocity
            new_body.diameter = diameter

        else:
            length = boundary['length']
            width = boundary['width']
            mass = boundary['mass']
            thrust = boundary['thrust']
            torque = boundary['torque']

            body, shape = self.bodies[body_id]
            position = body.position
            angle = body.angle

            # get shape, inertia, make body, assign body to shape
            new_shape = self.get_shape(boundary)
            inertia = self.get_inertia(new_shape, mass)
            new_body = pymunk.Body(mass, inertia)
            new_shape.body = new_body

            new_body.position = position
            new_body.angle = angle
            new_body.velocity = body.velocity
            new_body.angular_velocity = body.angular_velocity
            new_body.dimensions = (width, length)
            new_body.thrust = thrust
            new_body.torque = torque

        new_shape.elasticity = shape.elasticity
        new_shape.friction = shape.friction

        # swap bodies
        self.space.remove(body, shape)
        self.space.add(new_body, new_shape)

        # update body
        self.bodies[body_id] = (new_body, new_shape)

        if 'velocity' in boundary:
            self.set_velocity(body_id, boundary['velocity'])

    def update_bodies(self, bodies):
        # if an agent has been removed from the agents store,
        # remove it from space and bodies
        removed_bodies = [
            body_id for body_id in self.bodies.keys()
            if body_id not in bodies.keys()]
        for body_id in removed_bodies:
            body, shape = self.bodies[body_id]
            self.space.remove(body, shape)
            del self.bodies[body_id]

        # update agents, add new agents
        for body_id, specs in bodies.items():
            if body_id in self.bodies:
                self.update_body(body_id, specs)
            else:
                self.add_body_from_center(body_id, specs)

    def get_body_position(self, cell_id):
        body, shape = self.bodies[cell_id]
        return tuple(pos for pos in body.position)

    def get_body_positions(self):
        return {
            body_id: self.get_body_position(body_id)
            for body_id in self.bodies.keys()}



def test_multibody(
        total_time=2,
        agent_shape='circle',
        n_agents=1,
        jitter_force=1e1,
        velocity=10.0,  #  um / min
):

    bounds = [500, 500]
    center_location = [0.5*loc for loc in bounds]
    agents = {
        str(agent_idx): {
            'boundary': {
                'location': center_location,
                'volume': 15,
                'diameter': 30,
                'mass': 1,
                'velocity': velocity,
            }}
        for agent_idx in range(n_agents)
    }
    config = {
        'agent_shape': agent_shape,
        'jitter_force': jitter_force,
        'bounds': bounds,
        'barriers': False,
        'initial_agents': agents,
    }
    multibody = PymunkMultibody(config)

    # run simulation
    time = 0
    time_step = 1
    while time < total_time:
        time += time_step
        multibody.run(time_step)


if __name__ == '__main__':
    test_multibody(10)
