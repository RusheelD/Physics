import math
import random

import pyglet

NUM_PARTICLES = 20
COLLISION_DECAY = 0.8
PARTICLE_SIZE = 5
PARTICLE_MASS = 5e16
BASE_PARTICLE_CHARGE = 0  # 1e-19
WIN_WIDTH = 600
WIN_HEIGHT = 600
GROUND_LEVEL = 10
PLANET_MASS = 0  # 6e25
GRAVITY_CONSTANT = 6.6743 * 1e-11
ELECTRIC_CONSTANT = 8.9875 * 1e9
TOUCHING_THRESHOLD = 5


def sign(x: float) -> int:
    if (x > 0):
        return 1
    elif (x < 0):
        return -1
    return 0


class KinematicsComponent:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Kinematics:
    def __init__(self, mass: float, pos_x: float, pos_y: float, vel_x: float, vel_y: float):
        self.mass = mass
        self.position = KinematicsComponent(pos_x, pos_y)
        self.velocity = KinematicsComponent(vel_x, vel_y)
        self.forces: dict[str, KinematicsComponent] = {}

    def add_force(self, name: str, force_x: float, force_y: float):
        self.forces.update({name: KinematicsComponent(force_x, force_y)})

    def remove_force(self, name: str):
        if name in self.forces:
            self.forces.pop(name)

    def update(self, dt):
        force_sum_x = sum(map(lambda x: x.x, self.forces.values()))
        force_sum_y = sum(map(lambda x: x.y, self.forces.values()))

        acc_x = force_sum_x / self.mass
        acc_y = force_sum_y / self.mass

        self.velocity.x += acc_x * dt
        self.velocity.y += acc_y * dt

        if (abs(self.velocity.x) < 0.001):
            self.velocity.x = 0

        if (abs(self.velocity.y) < 0.001):
            self.velocity.y = 0

        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt


class Particle:
    particles = 0

    def __init__(self, x: float, y: float, charge: float = 0, name=f"Particle {particles}"):
        self.kinematics = Kinematics(PARTICLE_MASS, x, y, 0, 0)
        self.charge = charge
        self.name = name
        Particle.particles += 1

    def get_x(self):
        return self.kinematics.position.x

    def get_y(self):
        return self.kinematics.position.y

    def get_dist(self, other: 'Particle'):
        return max(((self.kinematics.position.x - other.get_x())**2 + (self.kinematics.position.y - other.get_y())**2)**(1/2), 1e-15)


class Simulation:
    def __init__(self):
        self.window = pyglet.window.Window(
            WIN_WIDTH, WIN_HEIGHT, caption="Physics Simulation")

        self.window.push_handlers(self)
        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(WIN_WIDTH, WIN_HEIGHT)

        self.particles = [Particle(
            random.random() * 600, random.random() * 600, BASE_PARTICLE_CHARGE) for _ in range(NUM_PARTICLES)]

        for particle in self.particles:
            particle.kinematics.add_force("gravity", 0, -1 * 98)

    def update(self, dt):
        for particle in self.particles:
            particle.kinematics.add_force("gravity", 0, -1 * PLANET_MASS * GRAVITY_CONSTANT *
                                          particle.kinematics.mass / (6.4e6 + particle.get_y() - GROUND_LEVEL)**2)
            gravity_x, gravity_y = 0, 0
            electric_x, electric_y = 0, 0
            for other in self.particles:
                if (abs(other.get_x() - particle.get_x()) <= TOUCHING_THRESHOLD * PARTICLE_SIZE and abs(other.get_y() - particle.get_y()) <= TOUCHING_THRESHOLD * PARTICLE_SIZE and particle.kinematics.mass > 0 and other.kinematics.mass > 0 and particle != other):
                    other.kinematics.position.x = particle.get_x()
                    other.kinematics.position.y = particle.get_y()

                    mx_1 = particle.kinematics.mass * particle.kinematics.velocity.x
                    my_1 = particle.kinematics.mass * particle.kinematics.velocity.y

                    mx_2 = other.kinematics.mass * other.kinematics.velocity.x
                    my_2 = other.kinematics.mass * other.kinematics.velocity.y

                    vel_x = (mx_1 + mx_2) / \
                        (particle.kinematics.mass + other.kinematics.mass)
                    vel_y = (my_1 + my_2) / \
                        (particle.kinematics.mass + other.kinematics.mass)

                    particle.kinematics.mass = (
                        particle.kinematics.mass + other.kinematics.mass) / 2
                    other.kinematics = particle.kinematics

                    other.kinematics.velocity.x = vel_x
                    other.kinematics.velocity.y = vel_y
                    continue
                if (particle != other):
                    dist = particle.get_dist(other)
                    angle = math.atan(dist) + math.pi/2
                    gravity = GRAVITY_CONSTANT * particle.kinematics.mass * \
                        other.kinematics.mass / dist**2
                    electric = ELECTRIC_CONSTANT * particle.charge * other.charge / dist**2

                    gravity_dir_x = 1 if other.get_x() >= particle.get_x() else -1
                    gravity_dir_y = 1 if other.get_y() >= particle.get_y() else -1

                    electric_dir_x = sign(other.get_x(
                    ) - particle.get_x()) * (-1 if sign(particle.charge) == sign(other.charge) else 1)
                    electric_dir_y = sign(other.get_y(
                    ) - particle.get_y()) * (-1 if sign(particle.charge) == sign(other.charge) else 1)

                    gravity_x += gravity * abs(math.cos(angle)) * gravity_dir_x
                    gravity_y += gravity * abs(math.sin(angle)) * gravity_dir_y
                    electric_x += electric * \
                        abs(math.cos(angle)) * electric_dir_x
                    electric_y += electric * \
                        abs(math.sin(angle)) * electric_dir_y

            particle.kinematics.add_force(
                "particle-gravity", gravity_x, gravity_y)
            particle.kinematics.add_force(
                "particle-electric", electric_x, electric_y)
        for particle in self.particles:
            if (particle.get_y() < GROUND_LEVEL):
                particle.kinematics.velocity.y *= -1 * COLLISION_DECAY
                particle.kinematics.position.y = GROUND_LEVEL
            particle.kinematics.update(dt)

        for particle in self.particles:
            particle.kinematics.remove_force(
                "particle-gravity")
            particle.kinematics.remove_force(
                "particle-electric")
            # particle.kinematics.remove_force("gravity")

    def on_draw(self):
        self.window.clear()
        self.background.blit(0, 0)
        for particle in self.particles:
            # print(particle.get_x(), particle.get_y())
            circle = pyglet.shapes.Circle(
                particle.get_x(), particle.get_y(), PARTICLE_SIZE, color=(0, 125, 255, 255))
            circle.draw()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/120.0)
        pyglet.app.run()


def main():
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
