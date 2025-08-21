import gui
from utils import FileHandler


if __name__ == "__main__":
    filehandler = FileHandler()
    ui = gui.TkinterUi(filehandler)
    ui.initialize()
    ui.run()