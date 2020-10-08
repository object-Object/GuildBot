from discord.ext import commands

from utils import errors


def trustee_only():
    async def predicate(ctx):
        if ctx.guild is not None:
            role = ctx.guild.get_role((await ctx.bot.database.get_settings(ctx.guild.id))["trustee_role"])
            if role not in ctx.author.roles and ctx.author.id != ctx.guild.owner.id:
                raise errors.NotTrustee()
        return True
    return commands.check(predicate)


def is_guild_owner():
    async def predicate(ctx):
        if ctx.guild is not None:
            if ctx.author.id != ctx.guild.owner.id:
                raise commands.CheckFailure("You must be the guild owner to run this command.")
        return True
    return commands.check(predicate)


def channel_in_category():
    async def predicate(ctx):
        if ctx.guild is not None:
            if ctx.channel.category is None:
                raise commands.CheckFailure("This command can only be run in a channel that is in a category.")
        return True
    return commands.check(predicate)
