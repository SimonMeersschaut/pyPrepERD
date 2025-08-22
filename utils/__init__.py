from gui.plot import InteractiveERDPlot
from .grid import create_grid
from .polygon import points_in_polygon
from .file_handler import IMAGES_PATH, CONFIG_PATH, TOF_FILE_PATH, BPARAMS_FILE_PATH, ATOMIC_WEIGHTS_TABLE_FILE
from .file_handler import FileHandler
from .config import Config


# TODO: remove to readme.md
HELP_TEXT = """
If you want to change configurations, head to the config folder of this program.
This folder contains:
    - Bparams.txt: has fitted data
    - config.yaml: settings for pyPrepERD
    - Tof.in: settings about the machine

The source code of this program can be found at `https://github.com/SimonMeersschaut/pyPrepERD`.
"""