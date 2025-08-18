import numpy as np
import utils
import analysis

def generate_b_params(a_params: list) -> np.array:
    """
    Fits `b_params` through the `a_params`
    as specified in the original program by Grazia [see Documentation for reference].
    """
    if type(a_params) != list:
        raise ValueError("`a_params` was not of type list.")

    b_params = []
    
    for channel_k in range(utils.Config.get_setting("tofchmin"), utils.Config.get_setting("tofchmax")):
        # per mass, calculate its energy for this channel

        x = []
        y = []
        for mass, a, c in a_params:
            energy = c/(channel_k)**2 + a
            x.append(mass)
            y.append(energy)
        
        # Now fit a linear function through the datapoints
        a, b = np.polyfit(x, y, 1) # f(x) = a*x + b

        # store the parameters in an output list
        b_params.append([a, b])
    
    b_params = np.array(b_params)

    # Number of rows
    n = b_params.shape[0]

    # Line numbers (1 to n)
    line_numbers = np.arange(1, n+1).reshape(-1, 1)

    # Column of zeros
    zeros = np.zeros((n, 1), dtype=b_params.dtype)

    # Concatenate: line number, zeros, then the original data
    result = np.hstack((line_numbers, zeros, b_params))

    return result

def save_b_params(b_params: np.array, filename: str) -> None:
    """
    TODO
    """
    # TODO: sanity checks
    
    analysis.dump_dataframe(b_params, filename)