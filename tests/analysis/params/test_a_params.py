# test_analysis.py
import numpy as np
import pytest
from analysis.params.a_params import cut_data_to_a_params

# TODO:
def test_cut_data_to_a_params_perfect_fit():
    # True function: f(t) = c/t^2 + a
    a_true, c_true = 2.0, 5.0
    t = np.linspace(1, 10, 50)
    y = c_true / (t**2) + a_true
    cut_data = np.column_stack((np.arange(len(t)), t, y))  # shape (N, 3)

    a, b, c = cut_data_to_a_params(cut_data)

    # assert np.isclose(a, a_true, atol=1e-8)
    # assert np.isclose(c, c_true, atol=1e-8)

# def test_cut_data_to_a_params_raises_on_bad_data():
#     # identical t-values make delta = 0
#     t = np.ones(5)
#     y = np.arange(5)
#     cut_data = np.column_stack((np.arange(len(t)), t, y))

#     with pytest.raises(ValueError, match="delta"):
#         cut_data_to_a_params(cut_data)