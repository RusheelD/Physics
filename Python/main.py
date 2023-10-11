import random

import pyglet

NUM_PARTICLES = 10
PARTICLE_SIZE = 5
PARTICLE_MASS = 1
WIN_WIDTH = 600
WIN_HEIGHT = 600
GROUND_LEVEL = 10
PLANET_GRAVITY = 9.8


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

    def update(self, dt):
        force_sum_x = sum(map(lambda x: x.x, self.forces.values()))
        force_sum_y = sum(map(lambda x: x.y, self.forces.values()))

        acc_x = force_sum_x * self.mass
        acc_y = force_sum_y * self.mass

        self.velocity.x += acc_x * dt
        self.velocity.y += acc_y * dt

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


class Simulation:
    def __init__(self):
        self.window = pyglet.window.Window(
            WIN_WIDTH, WIN_HEIGHT, caption="Physics Simulation")

        self.window.push_handlers(self)
        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(WIN_WIDTH, WIN_HEIGHT)

        self.particles = [Particle(
            random.random() * 600, random.random() * 600, 0) for _ in range(NUM_PARTICLES)]

        for particle in self.particles:
            particle.kinematics.add_force("gravity", 0, -1 * PLANET_GRAVITY)

    def update(self, dt):
        for particle in self.particles:
            particle.kinematics.update(dt)

    def on_draw(self):
        self.window.clear()
        self.background.blit(0, 0)
        for particle in self.particles:
            # print(particle.get_x(), particle.get_y())
            circle = pyglet.shapes.Circle(
                particle.get_x(), particle.get_y(), PARTICLE_SIZE, color=(0, 125, 255, 255))
            circle.draw()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()


def main():
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
