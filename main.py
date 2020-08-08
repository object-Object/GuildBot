import config

from bot import Bot

bot = Bot(command_prefix=config.prefix)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
