import pyglet

NUM_PARTICLES = 10
PARTICLE_SIZE = 20
PARTICLE_MASS = 1
WIN_WIDTH = 600
WIN_HEIGHT = 600
GROUND_LEVEL = 10
PLANET_GRAVITY = 9800


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


class Particle:
    particles = 0

    def __init__(self, x: float, y: float, charge: float = 0, name=f"Particle {particles}"):
        self.kinematics = Kinematics(PARTICLE_MASS, x, y, 0, 0)
        self.charge = charge
        self.name = name
        Particle.particles += 1


class Simulation:
    def __init__(self):
        self.window = pyglet.window.Window(
            WIN_WIDTH, WIN_HEIGHT, caption="Physics Simulation")

        self.window.push_handlers(self)


def main():
    pass


if __name__ == "__main__":
    main()
