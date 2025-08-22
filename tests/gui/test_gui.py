from utils import FileHandler
from unittest.mock import MagicMock, patch
import unittest
import gui


class TestGui(unittest.TestCase):
    @patch("tkinter.Tk", return_value=MagicMock())
    def test_start_gui(self, mock_tk):
        filehandler = FileHandler(remote_not_found_ok=True) # shared disk cannot be found on Github
        ui = gui.TkinterUi(filehandler, headless=True)
        # ui.initialize()
        # ui.run(block=False)