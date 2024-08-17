import math

import PIL.ImageDraw2
# import cored
from PIL import Image, ImageDraw
from typing import List
import platform

from numpy import dtype

import cored

import signal
import numpy as np
import sys
import time
#TODO: show time remaining

simulation_size = (1100, 900)

image = Image.new('RGB', simulation_size, color='black')
draw = ImageDraw.Draw(image)
max_steps = 10000
step_size = 0
keep_velocity = 0.999
GRAVITY_CONSTANT = 10
PARTICLE_MASS = 0.4
force_stop = False

class StaticBody:
    def __init__(self,x,y,mass, color, density=0.1):
        self.pos = np.array([x,y])
        self.mass = mass
        self.color = color
        self.density = density
        self.radius = int(math.sqrt(self.mass/(math.pi*self.density)))

        print(f"mass:{self.mass} radius:{self.radius}")

    def get_distance(self, pos):
        return np.linalg.norm(self.pos - pos)

    def get_distance_squared(self, x, y):
        return (x - self.x)**2 + (y - self.y)**2

    @property
    def x(self):
        return self.pos[0]
    @property
    def y(self):
        return self.pos[1]

def render_bodies(static_bodies: List[StaticBody], black = False):
    for body in static_bodies:
        if black:
            draw.circle(body.pos, body.radius,(0,0,0))
        else:
            draw.circle(body.pos, body.radius, body.color)


def render_gravity_basins(static_bodies: List[StaticBody]):
    current_pixel = 0
    black_pixels = 0

    pixels = image.load()

    for x in range(simulation_size[0]):
        for y in range(simulation_size[1]):
            if force_stop:
                return

            print(f"\rPixel: {current_pixel}/{simulation_size[0] * simulation_size[1]}  {round(current_pixel / (simulation_size[0] * simulation_size[1]) * 100)}%    black pixels: {black_pixels}", end='', flush=True)
            if current_pixel % 500 == 0:
                image.save("gravity_wells_friction_smallstep4.png")

            crashing_body = get_crashing_body(static_bodies, [x, y])

            if crashing_body is None:
                black_pixels+=1
                continue

            pixels[x, y] = crashing_body.color
            current_pixel += 1

def get_crashing_body(static_bodies: List[StaticBody], starting_position: list[2]) -> StaticBody:
    pos = np.array(starting_position, dtype=float)
    velocity = np.array([0,0], dtype=float)
    for body in static_bodies:
        if pos[0] == body.pos[0] and pos[1] == body.pos[1]:
            return body

    for step in range(max_steps):
        force = np.array([0,0], dtype=float)
        for body in static_bodies:
            force += gravity_force(body, pos)
            if body.get_distance_squared(pos[0], pos[1]) <= body.radius**2:
                return body

        velocity += force/PARTICLE_MASS
        pos += velocity

    return None



def render_trajectory(static_bodies: List[StaticBody], starting_position: list[2], radius = 1):
    pos = np.array(starting_position, dtype=float)
    velocity = np.array([0,0], dtype=float)
    for step in range(max_steps):
        force = np.array([0,0], dtype=float)
        for body in static_bodies:
            force += gravity_force(body, pos)
            if body.get_distance_squared(pos[0], pos[1]) <= body.radius**2:
                return

        velocity += force/PARTICLE_MASS
        pos += velocity


        if 0 <= pos[0] <= simulation_size[0] and 0 <= pos[1] <= simulation_size[1]:
            image.putpixel((int(pos[0]), int(pos[1])), (255,255,255))
            draw.circle(pos, radius, (255,255,255))


def net_gravity_force(bodies: List[StaticBody], position: np.ndarray) -> np.ndarray:
    net_force = np.zeros(2, dtype=float)
    for body in bodies:
        net_force += gravity_force(body, position)

    return net_force




def gravity_force(body: StaticBody, pos: np.ndarray) -> np.ndarray:
    distance = body.get_distance(pos)

    direction_vector = (body.pos - pos)/distance

    magnitude = GRAVITY_CONSTANT * body.mass / (distance**2)

    return direction_vector * magnitude



def on_exit(sig, frame):
    global force_stop
    force_stop = True

if __name__ == "__main__":
    print(platform.python_implementation())

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    # bodies = [StaticBody(100, 300, 10, (255,39,12)),
    #           StaticBody(250, 250, 5, (41,255,31)),
    #           StaticBody(150, 150, 12,(10,14, 241)),
    #           StaticBody(450, 150, 14,(200,14, 241))]
    bodies = [StaticBody(75, 75, 200, (255,39,12)),
              StaticBody(550, 45, 200, (41,255,31)),
              StaticBody(800, 400, 200,(10,14, 241))]
    cored.render_gravity_basins(bodies, image)
    render_bodies(bodies, black=True)
    # render_trajectory(bodies, starting_position=[1400,300], radius=5)
    image.save("gravity_wells_friction_smallstep4.png")
    image.show()

