import config
import discord
from discord.ext import commands

from bot import Bot
from help import GuildBotHelp

bot = Bot(command_prefix=config.prefix, help_command=GuildBotHelp())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.NotOwner):
		await ctx.send(embed=discord.Embed(
			title="You may not run this command!",
			description="You do not own this bot.",
			color=discord.Color(0xff0000)
		))

bot.run(config.token)
