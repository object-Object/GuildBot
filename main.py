import config
from bot import Bot
from utils.help import GuildBotHelp

bot = Bot(command_prefix=config.prefix, help_command=GuildBotHelp())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
