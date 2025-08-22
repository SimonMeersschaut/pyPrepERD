import yaml
import json
from .file_handler import FileHandler

with open("config/config.yaml") as info: # TODO: replace
    info_dict = yaml.load(info, Loader=yaml.Loader)

filehandler = FileHandler()

class Config:
    """
    This class handles configuration settings, by loading
    a .yaml file.
    """
    
    @classmethod
    def get_setting(cls, name: str) -> object:
        """This function returns the value of the setting with name `name."""
        return info_dict[name]

    @classmethod
    def get_polygon_history(cls):
        """Returns polygons that were drawn by this user in the past."""
        file_path = filehandler.get_root_path() / "userdata" / "polygon_history.json"
        if not filehandler.path_exists(file_path): # TODO: Replace
            with open(file_path, "w+") as f:
                f.write("{}")
            return {}

        with open(file_path, 'r') as f:
            return json.load(f)
    
    @classmethod
    def add_polygon_to_history(cls, atom, dir, polygon) -> None:
        history = cls.get_polygon_history()

        history.update(
        {
            dir+atom : {
                "dir": dir,
                "atom": atom,
                "polygon": polygon,
            }
        })

        file_path = filehandler.get_root_path() / "userdata" / "polygon_history.json"
        with open(file_path, "w+") as f:
            json.dump(history, f)