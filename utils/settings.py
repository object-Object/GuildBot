import copy
import json

import config

default_settings = {  # key: setting name, value: default value
    "thread_categories": [],
    "autoroles": [],
    "archive_category": None,
    "trustee_role": None,
    "welcome_channel": None,
    }


class Settings():
    def __init__(self):
        try:
            with open(config.settings_filename, "r") as f:
                file_json = json.load(f)
        except OSError:  # file doesn't exist yet
            file_json = copy.deepcopy(default_settings)
            with open(config.settings_filename, "w") as f:
                json.dump(file_json, f)
        for s in default_settings:
            setattr(self, s, file_json.pop(s))
        if file_json:  # file_json isn't empty after popping all the valid settings
            raise Exception(f"Unexpected entries in {config.settings_filename}")

    def save(self):
        """Write the current setting values to the json file."""
        file_json = {s: getattr(self, s) for s in default_settings}
        with open(config.settings_filename, "w") as f:
            json.dump(file_json, f)
