from discord.ext import commands

import sys
import traceback
import os

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

        for extension in [f for f in os.listdir('extensions') if f.endswith('.py')]:
            try:
                self.load_extension('extension/' + extension[:3])
            except Exception as e:
                print("Failed to load extention {}:".format(extension), file:sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
