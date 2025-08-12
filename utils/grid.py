import numpy as np
import math

SCALE = 1E1

def index_to_rect(x_index, y_index):
    return (x_index*SCALE, y_index*SCALE, (x_index+1)*SCALE-.1, (y_index+1)*SCALE-.1)

def create_grid(extended_data, x_index:int, y_index:int):
    """
    TODO: docs
    x_index, y_index define which indices are selected from the extended data frame. (i.e. which columns)
    """

    min_x = np.min(extended_data[:,x_index]) - 1
    max_x = np.max(extended_data[:,x_index]) + 1
    min_y = np.min(extended_data[:,y_index]) - 1
    max_y = np.max(extended_data[:,y_index]) + 1
    
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
        x, y = point[x_index], point[y_index]
        x_i, y_i = int(x), int(y)
        pixels[y_i][x_i] += 1
    
    return pixels