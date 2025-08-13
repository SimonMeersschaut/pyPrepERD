import numpy as np
import math

SCALE = 1E1

def index_to_rect(x_index, y_index):
    return (x_index*SCALE, y_index*SCALE, (x_index+1)*SCALE-.1, (y_index+1)*SCALE-.1)

def create_grid(extended_data, x_index:int, y_index:int):
    """
    Returns a two dimensional grid containing, for each [y][x], the number of points
    that are contained in that square.

    Parameters x_index, y_index define which indices are selected from the extended data frame. (i.e. which columns).
    This way, one can use this function to plot both mass versus time, and energy versus time.
    """

    # TODO: zet x=(x: 50-...) en y=(y: 0-...)

    # min_x = np.min(extended_data[:,x_index]) - 1
    max_x = np.max(extended_data[:,x_index]) + 1
    # min_y = np.min(extended_data[:,y_index]) - 1
    max_y = np.max(extended_data[:,y_index]) + 1
    
    #

    GRID_SIZE = (
        math.ceil(max_x),
        math.ceil(max_y)
    )

    pixels = np.zeros((GRID_SIZE[1], GRID_SIZE[0]))

    for point in extended_data:
        x, y = point[x_index], point[y_index]
        x_i, y_i = int(x), int(y)
        pixels[y_i][x_i] += 1
    
    return pixels