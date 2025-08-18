import numpy as np


def extended_data_to_a_params(extended_data: np.array):
    """
    TODO: docs
    """
    y = extended_data[:, 2]
    u = 1 / y
    x = extended_data[:, 0]

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