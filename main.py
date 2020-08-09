import config
import discord
from discord.ext import commands

from bot import Bot
from help import GuildBotHelp

bot = Bot(command_prefix=config.prefix, help_command=GuildBotHelp())

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
