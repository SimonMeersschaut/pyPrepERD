import numpy as np
from .tree import QuadTree

def extended_to_quad_tree(extended_data: np.array) -> QuadTree:
    #
    
    min_x = np.min(extended_data[:,1]) - 1
    max_x = np.max(extended_data[:,1]) + 1
    min_y = np.min(extended_data[:,2]) - 1
    max_y = np.max(extended_data[:,2]) + 1
    
    tree = QuadTree(
        (
            min_x,
            min_y,
            max_x - min_x,
            max_y - min_y,
        )
    )
    
    # append all points
    for index in range(len(extended_data)):
        tree.insert((extended_data[index][1], extended_data[index][2]))
    
    return tree
    # ttr.visualize(tree)