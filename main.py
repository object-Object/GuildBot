import config
import discord
from discord.ext import commands
import sqlite3

from bot import Bot
from utils.help import GuildBotHelp

bot = Bot(conn=sqlite3.connect(config.db), command_prefix=config.prefix, help_command=GuildBotHelp())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
