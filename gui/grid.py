import numpy as np



def create_grid(self, tree):
    """
    TODO: docs
    """
    GRID_SHAPE = (100, 100)

    pixels = np.zeros(GRID_SHAPE)

    for x_index in range(GRID_SHAPE[0]):
        for y_index in range(GRID_SHAPE[1]):
            rect = self.index_to_rect(x_index, y_index)
            contained_points = tree.containing_points(rect)
            pixels[x_index][y_index] = contained_points
    
    return pixels