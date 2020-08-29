import json

import config


class Settings():
    def __init__(self, settings=None):
        if settings is None:
            with open(config.settings_filename, "r") as f:
                settings = json.load(f)
        self.__dict__.update(settings)

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        with open(config.settings_filename, "w") as f:
            json.dump(self.__dict__, f)
