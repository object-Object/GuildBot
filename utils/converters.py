import discord
from discord.ext import commands


class CategoryConverter(commands.Converter):
    async def convert(self, ctx, argument):
        channel = discord.utils.find(lambda c: c.name.lower() == argument.lower(), ctx.guild.categories)
        if not isinstance(channel, discord.CategoryChannel):
            return await commands.CategoryChannelConverter().convert(ctx, argument)
        return channel


class TextChannelConverter(commands.Converter):
    async def convert(self, ctx, argument):
        channel = discord.utils.find(lambda c: c.name.lower() == argument.lower(), ctx.guild.text_channels)
        if not isinstance(channel, discord.TextChannel):
            return await commands.TextChannelConverter().convert(ctx, argument)
        return channel


class RoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        role = discord.utils.find(lambda r: r.name.lower() == argument.lower(), ctx.guild.roles)
        if not isinstance(role, discord.Role):
            return await commands.RoleConverter().convert(ctx, argument)
        return role


class ThreadConverter(commands.Converter):
    async def convert(self, ctx, argument):
        channel = discord.utils.find(lambda c: c.name.lower() == argument.lower(), ctx.guild.text_channels)
        if not isinstance(channel, discord.TextChannel):
            channel = await commands.TextChannelConverter().convert(ctx, argument)
        if not await ctx.bot.database.get_thread(channel.id):
            raise commands.BadArgument(f"{channel.mention} is not a thread.")
        return channel
