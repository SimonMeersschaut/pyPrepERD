from gui.plot import Plot
from .grid import create_grid
from .polygon import points_in_polygon
from .file_handler import FileHandler
from .config import Config
import os

HELP_TEXT = """
If you want to change configurations, head to the config folder of this program.
This folder contains:
    - Bparams.txt: has fitted data
    - config.yaml: settings for pyPrepERD
    - Tof.in: settings about the machine

The source code of this program can be found at `https://github.com/SimonMeersschaut/pyPrepERD`.
"""

WORKING_DIRECTORY = os.getcwd() + '/' # Root will be the working directory

IMAGES_PATH = WORKING_DIRECTORY + "images/"
CONFIG_PATH = WORKING_DIRECTORY + "config/"

TOF_FILE_PATH = CONFIG_PATH + "Tof.in"
BPARAMS_FILE_PATH = CONFIG_PATH + "Bparams.txt"
ATOMIC_WEIGHTS_TABLE_FILE = CONFIG_PATH + "atomic_weights_table.json"