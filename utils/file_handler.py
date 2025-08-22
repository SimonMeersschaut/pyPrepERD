from pathlib import Path
from utils import Log

class FolderNotFoundError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"The following folder could not be found: {path}")

class FolderNotFoundWarning(Warning):
    def __init__(self, path: Path):
        super().__init__(f"The following folder could not be found: {path}")


class FileHandler:
    def __init__(self, remote_path: Path = Path("W:\\"), remote_not_found_ok=False):
        self._root = Path.cwd()  # Use the current working directory as root
        self._remote = Path(remote_path)

        if not self._root.exists():
            raise FolderNotFoundError(self._root)

        if not self._remote.exists():
            if remote_not_found_ok:
                Log.warn(str(FolderNotFoundWarning(self._remote)) + "; we will use a stub for now.")
                self._remote = self._root / "example_remote"
            else:
                raise FolderNotFoundError(self._remote)

    @staticmethod
    def path_exists(path: Path) -> bool:
        """Check if a path exists as a file or folder."""
        return path.exists()

    @staticmethod
    def get_stem(path: Path) -> str:
        """Return the stem of a file (filename without extension)."""
        return path.stem

    @staticmethod
    def get_name(path: Path) -> str:
        """Return the name of a file (including extension)."""
        return path.name

    # Root and remote getters
    @property
    def root_path(self) -> Path:
        return self._root

    @property
    def remote_path(self) -> Path:
        return self._remote

    # Subfolder paths
    @property
    def images_path(self) -> Path:
        return self._root / "images"

    @property
    def config_path(self) -> Path:
        return self._root / "config"

    @property
    def transfer_ERD_path(self) -> Path:
        return self._remote / "transfer_ERD"

    @property
    def user_data_path(self) -> Path:
        return self._root / "userdata"


    # Specific file paths
    @property
    def mparams_path(self) -> Path:
        return  self.transfer_ERD_path / "erd_settings" / "Mparams.json"
    
    @property
    def tof_file_path(self) -> Path:
        return self.config_path / "Tof.in"

    @property
    def atomic_weights_table_file(self) -> Path:
        return self.config_path / "atomic_weights_table.json"
    
    @property
    def bparams_file_path(self) -> Path:
        return self._root / "config" / "Bparams.txt" # TODO: Replace with Mparams on remote
