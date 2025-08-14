import yaml

with open("config/config.yaml") as info:
    info_dict = yaml.load(info, Loader=yaml.Loader)

class Config:
    """
    This class handles configuration settings, by loading
    a .yaml file.
    """
    
    @classmethod
    def get_setting(cls, name: str) -> object:
        """This function returns the value of the setting with name `name."""
        return info_dict[name]