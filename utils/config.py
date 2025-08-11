import yaml

with open("config/settings.yaml") as info:
    info_dict = yaml.load(info, Loader=yaml.Loader)

class Config:
    
    @classmethod
    def get_setting(cls, name: str) -> object:
        return info_dict[name]