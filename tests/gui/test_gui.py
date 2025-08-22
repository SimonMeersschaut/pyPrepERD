from utils import FileHandler
import unittest
import gui


class TestGui(unittest.TestCase):
    def test_start_gui(self):
        filehandler = FileHandler(remote_not_found_ok=True) # shared disk cannot be found on Github
        ui = gui.TkinterUi(filehandler)
        # ui.initialize()
        # ui.run(block=False)