from matplotlib.path import Path
import numpy as np


# TODO: use x_index, y_index

def points_in_polygon(extended_data: list[float, float], polygon_vertices: list[ tuple[float, float] ], x_index: int = 1, y_index:int = 2) -> list:
    """
    Returns the points contained in a polygon.
    """
    path = Path(polygon_vertices)  # polygon as list of (x, y)
    mask = path.contains_points(extended_data[:, [x_index, y_index]])
    return extended_data[mask]