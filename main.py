import config
import discord
from bot import Bot
from utils.help import GuildBotHelp

intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix=config.prefix, help_command=GuildBotHelp(), intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
