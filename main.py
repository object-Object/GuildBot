import discord

from bot import Bot

bot = Bot(command_prefix="/")

@bot.group(invoke_without_command=True)
async def extensions(ctx):
    ctx.say("""`/extensions load <extension>` Loads specified extension
    `/extensions unload <extension>` Unloads specified extension
    `/extensions reload <extension>` Reloads specified extension""")

@extensions.command()
async def load(ctx, extension: str):
    try:
        self.load_extension('extension/' + extension[:3])

        ctx.send("Loaded extension {} successfully".format(extension))
    except Exception as e:
        ctx.send("Failed to load extension {}:\n{}".format(extension, e))

        print("Failed to load extension {}:".format(extension), file:sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@extensions.command()
async def unload(ctx, extension: str):
    try:
        self.unload_extension('extension/' + extension[:3])

        ctx.send("Unloaded extension {} successfully".format(extension))
    except Exception as e:
        ctx.send("Failed to unload extension {}:\n{}".format(extension, e))

        print("Failed to unload extension {}:".format(extension), file:sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@extensions.command()
async def reload(ctx, extension: str):
    try:
        self.load_extension('extension/' + extension[:3])
        self.unload_extension('extension/' + extension[:3])

        ctx.send("Reloaded extension {} successfully".format(extension))
    except Exception as e:
        ctx.send("Failed to reload extension {}:\n{}".format(extension, e))

        print("Failed to unload extension {}:".format(extension), file:sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.run(REPLACE_WITH_DISCORD_TOKEN)
