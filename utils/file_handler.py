from pathlib import Path

# TODO: Replace all file paths

class FolderNotFoundError(Exception):
    def __init__(self, path: Path):
        super().__init__("The following folder could not be found:" + str(path))

class FileHandler:
    def __init__(self):
        self._root = "" # root of project
        self._remote = "W:\\"
        
        if not self.path_exists(self._root):
            raise FolderNotFoundError(self._root)

        if not self.path_exists(self._remote):
            raise FolderNotFoundError(self._remote)
    
    def path_exists(self, path: Path):
        return path.is_dir()
    
