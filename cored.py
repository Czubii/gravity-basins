from idlelib.run import manage_socket

import main
from main import *
import multiprocessing as mp
from multiprocessing import Manager
from PIL import Image

slices = [5,5]
slice_size = (int(main.simulation_size[0] / slices[0]), int(main.simulation_size[1] / slices[1]))
#TODO: make it so maximum like 10 proceses get initiated at once
class ImageSlice:
    def __init__(self, start_pos, image):
        self.start_pos = start_pos
        self.image = image

def render_slice(queue, start_x, end_x, start_y, end_y, static_bodies, save=False):
    try:
        image_slice = Image.new('RGB', slice_size, color='black')
        pixels = image_slice.load()
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                crashing_body = get_crashing_body(static_bodies, [x, y])
                if crashing_body is None:
                    continue
                pixels[x-start_x, y-start_y] = crashing_body.color

        output = ImageSlice([start_x, start_y], image_slice)
        queue.put(output)

    except Exception as e:
        print(f"Error in render_slice: {e}")
        queue.put(None)  # Put a sentinel value to indicate an error
    finally:
        queue.put(None)



def render_gravity_basins(static_bodies: List[StaticBody], output_image: Image):
    queues = []
    processes = []
    manager = Manager()
    save = True
    for x_slice in range(slices[0]):
        for y_slice in range(slices[1]):
            queue = manager.Queue()
            queues.append(queue)
            args = (queue,
                    x_slice*slice_size[0], ((x_slice+1)*slice_size[0]),
                    y_slice*slice_size[1], ((y_slice+1)*slice_size[1]),
                    static_bodies, save)
            processes.append(mp.Process(target=render_slice,args=args))
            processes[-1].start()
            save = False

    while any(p.is_alive() for p in processes):
        running_processes = sum(p.is_alive() for p in processes)
        print(f"\rSlices rendered: {len(processes)-running_processes}/{len(processes)}", end='', flush=True)
        time.sleep(1)

    image_slices = []
    for p in processes:
        p.join()

    for q in queues:
        image_slices.append(q.get())

    for image_slice in image_slices:
        output_image.paste(image_slice.image, image_slice.start_pos)


