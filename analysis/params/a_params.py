import numpy as np
from analysis import load_dataframe
import utils
import os
import json
import glob


def generate_a_params(project: str) -> str:
    """
    Generates a list with `a-params` based on measurements and a cut (=polygon)
    all located in the project folder.
    """
    if not os.path.exists(project):
        raise FileNotFoundError(f"Project folder `{project}` not found.")

    # Per measurement, open the data
    subfolders = [f.path for f in os.scandir(project) if f.is_dir() and not "raw" in f.path[0]] # TODO: `in` aanpassen

    a_params = []

    for subfolder in subfolders:
        # Open cut file
        cut_files = [file for file in glob.glob(subfolder+"/Cut-files/*.*") if not ".json" in file]
        if len(cut_files) != 1:
            raise RuntimeError() # TODO
        
        element = cut_files[0].split('/')[-1].split('\\')[-1].split('.')[-1]
        # lookup mass in table
        with open(utils.ATOMIC_WEIGHTS_TABLE_FILE, 'r') as f:
            data = json.load(f)
        mass = [block for block in data[1:] if block[0] == element][0][1] # Returns the mass of `element`

        cut_data = load_dataframe(cut_files[0])

        a, c = cut_data_to_a_params(cut_data)
        a_params.append([mass, a, c])
    
    if len(set([block[0] for block in a_params])) == 1:
        # all masses are equal
        raise ValueError("All masses were equal. Select at least one different mass.")

    return a_params

def cut_data_to_a_params(cut_data: np.array) -> tuple:
    x = cut_data[:, 1]
    y = cut_data[:, 2]
    u = 1 / (x**2)

    n = len(u)
    S_u = np.sum(u)
    S_uu = np.sum(u**2)
    S_y = np.sum(y)
    S_uy = np.sum(u*y)

    delta = n*S_uu - S_u**2
    if delta == 0:
        raise ValueError("`delta` was zero, insufficient data for the fit.")

    c = (n*S_uy - S_u*S_y) / delta
    a = (S_y - c*S_u) / n
    return a, c
