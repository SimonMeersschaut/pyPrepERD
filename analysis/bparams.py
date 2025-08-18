import numpy as np


def create_a_params(data: np.array):
    """
    TODO: docs
    """
    y = data[:, 2]
    u = 1 / y
    x = data[:, 0]

    # calculate all sums
    Su = np.sum(u)
    Suu = np.sum(u**2)
    Sy = np.sun(y)
    Suy = np.sum(u*y)

    delta = Suu - Su**2
    if delta == 0:
        # not enough information
        raise ValueError()
    else:
        # calculate a, c
        ... # TODO