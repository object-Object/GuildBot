import discord
from discord.ext import commands
import traceback
import sys

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        command_not_run = "Command couldn't be run!"
        command_failed = "Command failed!"

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored_errors = (commands.CommandNotFound,)
        error = getattr(error, "original", error)

        if isinstance(error, ignored_errors):
            return

        if hasattr(ctx.command, "handled_errors") and isinstance(error, ctx.command.handled_errors):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(embed=discord.Embed(
                title=command_not_run,
                description=f"`{self.bot.command_prefix}{ctx.command}` has been disabled.",
                color=discord.Color(0xff0000)))

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(embed=discord.Embed(
                    title=command_not_run,
                    description=f"`{self.bot.command_prefix}{ctx.command}` cannot be used in Private Messages.",
                    color=discord.Color(0xff0000)))
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.NotOwner):
            await ctx.send(embed=discord.Embed(
                title=command_not_run,
                description=f"`{self.bot.command_prefix}{ctx.command}` may only be used by the bot owner, and you do not own this bot.",
                color=discord.Color(0xff0000)))

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title=command_failed,
                description=f"{error}\nCommand usage: `{self.bot.command_prefix}{ctx.command.qualified_name} {ctx.command.signature}`",
                color=discord.Color(0xff0000)))

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title=command_not_run,
                description=str(error),
                color=discord.Color(0xff0000)))

        else:
            print("\nIgnoring exception in command {}:".format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))

def teardown(bot):
    bot.remove_cog("CommandErrorHandler")