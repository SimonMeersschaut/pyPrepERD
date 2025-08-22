from pathlib import Path
import os

IMAGES_PATH = Path("images")

WORKING_DIRECTORY = Path(os.getcwd()) # Root will be the working directory

IMAGES_PATH = WORKING_DIRECTORY / "images"
CONFIG_PATH = WORKING_DIRECTORY / "config"

TOF_FILE_PATH = CONFIG_PATH / "Tof.in"
BPARAMS_FILE_PATH = CONFIG_PATH / "Bparams.txt" # TODO: remove
ATOMIC_WEIGHTS_TABLE_FILE = CONFIG_PATH / "atomic_weights_table.json"

# TODO: Replace all file paths

class FolderNotFoundError(Exception):
    def __init__(self, path: Path):
        super().__init__("The following folder could not be found:" + str(path))

class FolderNotFoundWarning(Warning):
    def __init__(self, path: Path):
        super().__init__("The following folder could not be found:" + str(path))


class FileHandler:
    def __init__(self, remote_not_found_ok=False):
        self._root = Path("") # root of project
        self._remote = Path("W:\\")
        
        if not self.path_exists(self._root):
            raise FolderNotFoundError(self._root)

        if not self.path_exists(self._remote):
            if remote_not_found_ok:
                # No problem, you are probably running tests on Github 👍
                print(FolderNotFoundWarning(self._remote))
                self._remote = self._root / "example_remote"
            else:
                # Whoops, the disk is not connected
                raise FolderNotFoundError(self._remote)
    
    def path_exists(self, path: Path):
        return path.is_dir() or path.is_file()
    

    def get_stem(self, path: Path):
        """
        "example.txt" -> "example"
        """
        return path.stem

    def get_name(self, path: Path):
        """
        "example.txt" -> "example.txt"
        """
        return path.name

    def get_remote_path(self):
        return self._remote

    def get_root_path(self):
        return self._root

    def get_mparams_path(self):
        return self._remote / "transfer_ERD" / "erd_settings" / "Mparams.json"

    