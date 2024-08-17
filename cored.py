from symtable import Class

from main import *
import multiprocessing as mp



def render_gravity_basins(static_bodies: List[StaticBody]):
    slice_size = (256, 144)
    def render_slice(start_x, end_x, start_y, end_y, image):

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                crashing_body = get_crashing_body(static_bodies, [x, y])
                if crashing_body is None:
                    continue
                image.putpixel((x, y), crashing_body.color)


    processes = []

    for x_slice in range(simulation_size[0] / slice_size[0]):
        for y_slice in range(simulation_size[1] / slice_size[1]):
            args = (x_slice*slice_size[0], ((x_slice+1)*slice_size[0]-1),
                    y_slice*slice_size[1], ((y_slice+1)*slice_size[1]-1))
            processes.append(mp.Process(target=render_slice,args=args))
            processes[-1].start()

    for p in processes:
        p.join()

