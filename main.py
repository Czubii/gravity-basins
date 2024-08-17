import math

import PIL.ImageDraw2
# import cored
from PIL import Image, ImageDraw
from typing import List
import platform; print(platform.python_implementation())
import signal
import numpy as np
import sys
import time
#TODO: show time remaining

simulation_size = (2500, 2500)

image = Image.new('RGB', simulation_size, color='black')
draw = ImageDraw.Draw(image)
max_steps = 10000000
step_size = 0.1
keep_velocity = 0.999

force_stop = False

class StaticBody:
    def __init__(self,x,y,mass, color, density=0.1):
        self.x = x
        self.y = y
        self.mass = mass
        self.color = color
        self.density = density
        self.radius = int(math.sqrt(self.mass/(math.pi*self.density)))

        print(f"mass:{self.mass} radius:{self.radius}")

    def get_distance(self, x, y):
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

    def get_distance_squared(self, x, y):
        return (x - self.x)**2 + (y - self.y)**2

def render_bodies(static_bodies: List[StaticBody]):
    for body in static_bodies:

        draw.circle([body.x,body.y],body.radius,(0,0,0))


def render_gravity_basins(static_bodies: List[StaticBody]):
    current_pixel = 0
    black_pixels = 0

    pixels = image.load()

    for x in range(simulation_size[0]):
        for y in range(simulation_size[1]):
            if force_stop:
                return

            if current_pixel % 100 == 0:
                print(f"\rPixel: {current_pixel}/{simulation_size[0] * simulation_size[1]}  {round(current_pixel / (simulation_size[0] * simulation_size[1]) * 100)}%    black pixels: {black_pixels}", end='', flush=True)

            crashing_body = get_crashing_body(static_bodies, [x, y])

            if crashing_body is None:
                black_pixels+=1
                continue

            pixels[x, y] = crashing_body.color
            current_pixel += 1

def get_crashing_body(static_bodies: List[StaticBody], starting_position: list[2]) -> StaticBody:
    pos = starting_position

    for body in static_bodies:
        if pos[0] == body.x and pos[1] == body.y:
            return body

    velocity = [0, 0]

    for step in range(max_steps):

        acting_force = np.array([0,0])
        for body in static_bodies:
            distance_squared = body.get_distance_squared(pos[0], pos[1])
            force_x = (body.x-pos[0])/distance_squared * body.mass
            force_y = (body.y-pos[1])/distance_squared * body.mass

            acting_force[0] += force_x
            acting_force[1] += force_y
            if distance_squared <= body.radius**2:
                return body

        velocity[0] = velocity[0] * keep_velocity + acting_force[0]
        velocity[1] = velocity[1] * keep_velocity + acting_force[1]
        pos[0] += velocity[0]
        pos[1] += velocity[1]

    return None



def render_trajectory(static_bodies: List[StaticBody], starting_position: list[2]):
    pos = starting_position
    velocity = [0,0]
    for step in range(max_steps):
        if 0 <= pos[0] <= simulation_size[0] and 0 <= pos[1] <= simulation_size[1]:
            image.putpixel((int(pos[0]), int(pos[1])), (255,255,255))

        acting_force = [0,0]
        for body in static_bodies:
            distance_squared = body.get_distance_squared(pos[0], pos[1])
            force_x = (body.x-pos[0])/distance_squared * body.mass * step_size
            force_y = (body.y-pos[1])/distance_squared * body.mass * step_size

            acting_force[0] += force_x
            acting_force[1] += force_y
            if distance_squared <= body.radius**2:
                return
        velocity[0] += acting_force[0]
        velocity[1] += acting_force[1]
        pos[0] += velocity[0]
        pos[1] += velocity[1]

def on_exit(sig, frame):
    global force_stop
    force_stop = True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    # bodies = [StaticBody(100, 300, 10, (255,39,12)),
    #           StaticBody(250, 250, 5, (41,255,31)),
    #           StaticBody(150, 150, 12,(10,14, 241)),
    #           StaticBody(450, 150, 14,(200,14, 241))]
    bodies = [StaticBody(100, 100, 2000, (255,39,12)),
              StaticBody(250, 250, 2000, (41,255,31)),
              StaticBody(400, 400, 2000,(10,14, 241))]
    render_gravity_basins(bodies)
    render_bodies(bodies)
    # render_trajectory(bodies, starting_position=[1400,300])
    image.save("gravity_wells_friction_smallstep.png")

