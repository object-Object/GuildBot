import config
import discord
from discord.ext import commands
import sqlite3

from bot import Bot
from utils.help import GuildBotHelp

bot = Bot(command_prefix=config.prefix, help_command=GuildBotHelp())

conn = sqlite3.connect(config.db)
bot.conn = conn
# create db tables if they don't exist already
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS threads (channel_id, author_id)")
conn.commit()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

bot.run(config.token)
