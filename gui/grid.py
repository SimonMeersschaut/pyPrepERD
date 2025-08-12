import numpy as np
import math

SCALE = 1E1

def index_to_rect(x_index, y_index):
    return (x_index*SCALE, y_index*SCALE, (x_index+1)*SCALE-.1, (y_index+1)*SCALE-.1)

def create_grid(tree):
    """
    TODO: docs
    """

    GRID_SIZE = (
        math.ceil(tree.rect[2]),
        math.ceil(tree.rect[3])
    )

    # GRID_SIZE = (
    #     100, # x
    #     50, # y
    # )

    pixels = np.zeros((GRID_SIZE[1], GRID_SIZE[0]))

    for x_index in range(GRID_SIZE[0]):
        for y_index in range(GRID_SIZE[1]):
            rect = index_to_rect(x_index, y_index)
            contained_points = tree.containing_points(rect)
            # print(contained_points)
            pixels[y_index][x_index] = contained_points
    
    return pixels