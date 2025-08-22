import numpy as np
import utils
import analysis
from .a_params import model
import matplotlib.pyplot as plt

class AbortedError(Exception):
    ...

MINIMAL_M1 = 1E-8

def generate_m_params(a_params: list) -> np.array:
    """
    Fits `m_params` using the `a_params`
    as specified in the original program by Grazia [see folder `Documentation/` for reference].
    Modification: instead of a parabola, a piece wise function was constructed
    using two linear functions:
    
    f(x) = { f1(x), x > piece_wise_split
           { f2(x), x <= piece_wise_split
    f1(x) = m1*x + c1
    f2(x) = m2*x + c2
    """
    
    if type(a_params) != list:
        raise ValueError("`a_params` was not of type list.")

    m_params = []
    
    for time_of_flight_channel in range(utils.Config.get_setting("tofchmin"), utils.Config.get_setting("tofchmax")):
        # per mass, calculate its energy for this channel

        regular_points_x = []
        regular_points_y = []
        point_1 = None
        for mass, a1, a2, a3 in a_params:
            energy = model(time_of_flight_channel, a1, a2, a3)

            if mass == 1:
                point_1 = [energy, mass]
            else:
                regular_points_x.append(energy)
                regular_points_y.append(mass)

        # Now fit a linear function through the datapoints

        # f1(x) = m1*x + c1
        # f2(x) = m2*x + c2
        m1, c1 = np.polyfit(regular_points_x, regular_points_y, 1) # returns (m1, m2)

        if m1 < MINIMAL_M1:
            # not possible: function must be continiously ascending
            m1 = MINIMAL_M1

        # Try an aditional fit
        try:
            if point_1 is None:
                raise AbortedError()
            min_index = np.argmin(regular_points_x)
            x_min = regular_points_x[min_index]
            y_min = regular_points_y[min_index]
            piece_wise_split = x_min 

            # (point_1[0], point_1[1]) & (x_min, m1*x_min + c)
            m2 = (point_1[1] - (m1*x_min + c1)) / (point_1[0] - x_min)
            # m2 = (y_min - (m1*x_min + c1))/(x_min - point_1[0]) # m = delta_y / delta_x
            c2 = y_min - m2*x_min
                # f(x) = { f1(x), x > piece_wise_split
                #        { f2(x), x <= piece_wise_split
            if m2 > m1:
                # point is lower than initial fit,
                # we exclude this from the fit
                raise AbortedError()
            if m2 < 0:
                m2 = 0
                c2 = m1*x_min + c1
        except AbortedError:
            m2 = m1
            c2 = c1
            piece_wise_split = 0 # any arbitrary number, element of R, would work here (since f1=f2 here)
        
        # if time_of_flight_channel % 500 == 1:
        #     _create_channel_plot(regular_points_x+[point_1[0]], regular_points_y+[point_1[1]], (m1, c1, m2, c2, piece_wise_split), title=f"TOF channel = {time_of_flight_channel}")
        
        # store the parameters in an output list
        m_params.append([m1, c1, m2, c2, piece_wise_split])
    
    return m_params


def save_m_params(m_params: np.array, filename: str) -> None:
    """
    TODO
    """
    # TODO: sanity checks
    analysis.dump_json(m_params, filename)

def fit_function(x, m1, c1, m2, c2, piece_wise_split):
    return np.where(
        x > piece_wise_split,
        m1 * x + c1,
        m2 * x + c2
    )

def _create_channel_plot(x, y, params, title):
    # Generate smooth x values for plotting the curve
    x_fit = np.linspace(np.min(x), np.max(x))
    y_fit = fit_function(x_fit, *params)
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color="blue", label="Data points", alpha=0.7)
    plt.plot(x_fit, y_fit, color="red", label=f"Fit: {params}")

    plt.xlabel("Energy Channel")
    plt.ylabel("Mass [amu]")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()