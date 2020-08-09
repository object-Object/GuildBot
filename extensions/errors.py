import discord
import traceback
import sys
from discord.ext import commands


class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		embedTitle = "Command couldn't be run!"

		if hasattr(ctx.command, "on_error"):
			return

		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		ignoredErrors = (commands.CommandNotFound)
		error = getattr(error, "original", error)

		if isinstance(error, ignoredErrors):
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(embed=discord.Embed(
				title=embedTitle,
				description=f"`{self.bot.command_prefix}{ctx.command}` has been disabled.",
				color=discord.Color(0xff0000)
			))

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(embed=discord.Embed(
					title=embedTitle,
					description=f"`{self.bot.command_prefix}{ctx.command}` cannot be used in Private Messages.",
					color=discord.Color(0xff0000)
				))
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.NotOwner):
			await ctx.send(embed=discord.Embed(
				title=embedTitle,
				description=f"`{self.bot.command_prefix}{ctx.command}` may only be used by the bot owner, and you do not own this bot.",
				color=discord.Color(0xff0000)
			))

		else:
			print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
	bot.add_cog(CommandErrorHandler(bot))
