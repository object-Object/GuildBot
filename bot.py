from discord.ext import commands

import sys
import traceback
import os
import config

class Bot(commands.Bot):
    def __init__(self, conn, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = conn

        for extension in [f for f in os.listdir("extensions") if f.endswith(".py")]:
            try:
                self.load_extension("extensions." + extension[:-3])
            except Exception as e:
                print(f"Failed to load extension {extension}:", file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


