import numpy as np
import math

SCALE = 1E1

def index_to_rect(x_index, y_index):
    return (x_index*SCALE, y_index*SCALE, (x_index+1)*SCALE-.1, (y_index+1)*SCALE-.1)

def create_grid(extended_data):
    """
    TODO: docs
    """

    min_x = np.min(extended_data[:,1]) - 1
    max_x = np.max(extended_data[:,1]) + 1
    min_y = np.min(extended_data[:,2]) - 1
    max_y = np.max(extended_data[:,2]) + 1
    
    #

    GRID_SIZE = (
        math.ceil(max_x),
        math.ceil(max_y)
    )

    # GRID_SIZE = (
    #     100, # x
    #     50, # y
    # )

    pixels = np.zeros((GRID_SIZE[1], GRID_SIZE[0]))

    for point in extended_data:
        x, y = point[1], point[2]
        x_index, y_index = int(x), int(y)
        pixels[y_index][x_index] += 1
    
    return pixels