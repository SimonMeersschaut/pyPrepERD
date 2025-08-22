from analysis import load_dataframe
from utils.grid import create_grid
from gui.plot import Plot
import numpy as np
from scipy.optimize import curve_fit
import utils
import os
from pathlib import Path
import json
import glob


def generate_a_params(project: str, make_plot=True) -> str:
    """
    Generates a list with `a-params` based on measurements and a cut (=polygon)
    all located in the project folder.

    Visualize this process as one moon fitting using a parabola.
    """
    if not os.path.exists(project):
        raise FileNotFoundError(f"Project folder `{project}` not found.")

    # Per measurement, open the data
    subfolders = [f.path for f in os.scandir(project) if f.is_dir() and not "raw" in f.path[0]] # TODO: `in` aanpassen

    a_params = []

    for subfolder in subfolders:
        # Open cut file
        cut_files = [file for file in glob.glob(subfolder+"/*.*") if not ".json" in file]
        if len(cut_files) > 1:
            raise RuntimeError(f"More thant one cut file per measurement found {subfolder}.")
        elif len(cut_files) == 0:
            raise RuntimeError(f"No cut files found in measurement {subfolder}.")
        cut_file = Path(cut_files[0])
        
        element = cut_file.suffix[1:]
        # lookup mass in table
        with open(utils.ATOMIC_WEIGHTS_TABLE_FILE, 'r') as f:
            data = json.load(f)
        try:
            mass = [block for block in data[1:] if block[0] == element][0][1] # Returns the mass of `element`
        except IndexError:
            raise ValueError(f"Element {element} was not found in the atomic_weights_table.")

        cut_data = load_dataframe(cut_files[0])
        a1, a2, a3 = cut_data_to_a_params(cut_data)
        
        # Create plot
        # _create_plot(cut_data, subfolder, a1, a2, a3)

        # energy = model(utils.Config.get_setting("tofchmin"), a1, a2, a3)
        # if energy > 88419520:
        #     continue

        a_params.append([mass, a1, a2, a3])
    
    if len(set([block[0] for block in a_params])) == 1:
        # all masses are equal
        raise ValueError("All masses were equal. Select at least one different mass.")

    return a_params

# Define the model function
def model(t, a1, a2, a3):
    return a1 + a2 * (1.0 / (t - a3))**2

def cut_data_to_a_params(cut_data: np.array) -> tuple:
    x = cut_data[:, 0]  # tof (channel)
    y = cut_data[:, 1]  # Energy


    # Provide a rough initial guess for the parameters
    a1_guess = np.mean(y)
    a2_guess = (np.max(y) - np.min(y)) * (np.mean(x)**2)
    a3_guess = np.min(x) / 2
    p0 = [a1_guess, a2_guess, a3_guess]

    # Fit using nonlinear least squares
    popt, _ = curve_fit(model, x, y, p0=p0, maxfev=10000)

    a1, a2, a3 = popt

    if a2 <= 0:
        raise RuntimeError("Fit values were non-sensical.")

    return a1, a2, a3

def _create_plot(cut_data, subfolder, a1, a2, a3):
    plot = Plot()
    grid, extent = create_grid(cut_data, x_index=0, y_index=1, downscale=True) # (tof, energy)
    plot.extent = extent
    plot.set_data(grid, None, f"Fit {Path(subfolder).name} {a1:.2f} + {a2:.2f} * (1/x-{a3:.2f})")
    plot.create_plot()

    x = np.arange(1600, 7E4, 1E2)
    plot.polygon_line.set_data(x, model(x, a1, a2, a3))
    plot.fig.canvas.restore_region(plot.background)
    plot.ax.draw_artist(plot.polygon_line)
    # Blit the updated axes to the canvas
    plot.fig.canvas.blit(plot.ax.bbox)
    plot.fig.canvas.flush_events()

    plot.save("output.png")
    plot.show()