import numpy as np
import math
from collections import Counter

SCALE = 1E1

def index_to_rect(x_index, y_index):
    return (x_index*SCALE, y_index*SCALE, (x_index+1)*SCALE-.1, (y_index+1)*SCALE-.1)


def create_grid(extended_data, x_index:int, y_index:int, downscale:bool=False, target_size:int=1000):
    x_vals = extended_data[:, x_index]
    y_vals = extended_data[:, y_index]

    min_x, max_x = np.min(x_vals), np.max(x_vals)
    min_y, max_y = np.min(y_vals), np.max(y_vals)

    if downscale:
        GRID_SIZE = (target_size, target_size)
        pixels = np.zeros(GRID_SIZE, dtype=np.int32)

        x_scaled = ((x_vals - min_x) / (max_x - min_x + 1e-12) * (target_size - 1)).astype(int)
        y_scaled = ((y_vals - min_y) / (max_y - min_y + 1e-12) * (target_size - 1)).astype(int)

        for x_i, y_i in zip(x_scaled, y_scaled):
            pixels[y_i, x_i] += 1

        extent = [min_x, max_x, min_y, max_y]

    else:
        GRID_SIZE = (math.ceil(max_x) + 1, math.ceil(max_y) + 1)
        pixels = np.zeros((GRID_SIZE[1], GRID_SIZE[0]), dtype=np.int32)

        for x, y in zip(x_vals, y_vals):
            x_i, y_i = int(x), int(y)
            pixels[y_i, x_i] += 1

        extent = [0, GRID_SIZE[0], 0, GRID_SIZE[1]]

    return pixels, extent