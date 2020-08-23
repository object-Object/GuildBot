import discord
from discord.ext import commands

class CategoryConverter(commands.Converter):
    async def convert(self, ctx, argument):
        channel = discord.utils.find(lambda c: c.name.lower()==argument.lower(), ctx.guild.categories)
        if not isinstance(channel, discord.CategoryChannel):
            return await commands.CategoryChannelConverter().convert(ctx, argument)
        return channel

class ThreadConverter(commands.Converter):
    async def convert(self, ctx, argument):
        channel = discord.utils.find(lambda c: c.name.lower()==argument.lower(), ctx.guild.text_channels)
        if not isinstance(channel, discord.TextChannel):
            return await commands.TextChannelConverter().convert(ctx, argument)
        return channel