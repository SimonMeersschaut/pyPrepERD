from utils import FileHandler
import gui


if __name__ == "__main__":
    filehandler = FileHandler()
    ui = gui.TkinterUi(filehandler)
    ui.initialize()
    ui.run()