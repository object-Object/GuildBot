import discord
import os
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=["ext"], brief="Lists all extensions in the bot, loaded or unloaded.")
    @commands.is_owner()
    async def extensions(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="List of extensions",
            description=f"`{'`, `'.join(sorted([f[:-3] for f in os.listdir('extensions') if f.endswith('.py')]))}`",
            color=discord.Color(0x007fff)))

    @extensions.command(brief="Loads an extension by name.")
    @commands.is_owner()
    async def load(self, ctx, extension: str):
        try:
            self.bot.load_extension("extensions." + extension)
        except commands.ExtensionError as e:
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=f"Failed to load extension `{extension}`:```\n" + str(e) + "```",
                color=discord.Color(0xff0000)))
        else:
            await ctx.send(embed=discord.Embed(
                description=f"Successfully loaded extension `{extension}`.",
                color=discord.Color(0x007fff)))

    @extensions.command(brief="Unloads an extension by name.")
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        if extension=="owner":
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=f"Extension `owner` cannot be unloaded.",
                color=discord.Color(0xff0000)))
            return

        try:
            self.bot.unload_extension("extensions." + extension)
        except commands.ExtensionError as e:
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=f"Failed to unload extension `{extension}`:```\n" + str(e) + "```",
                color=discord.Color(0xff0000)))
        else:
            await ctx.send(embed=discord.Embed(
                description=f"Successfully unloaded extension `{extension}`.",
                color=discord.Color(0x007fff)))

    @extensions.command(aliases=["r"], brief="Reloads an extension by name. Rolls back the changes if there is an error.")
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        try:
            self.bot.reload_extension("extensions." + extension)
        except commands.ExtensionError as e:
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=f"Failed to reload extension `{extension}`:```\n" + str(e) + "```",
                color=discord.Color(0xff0000)))
        else:
            await ctx.send(embed=discord.Embed(
                description=f"Successfully reloaded extension `{extension}`.",
                color=discord.Color(0x007fff)))

def setup(bot):
    bot.add_cog(Owner(bot))

def teardown(bot):
    bot.remove_cog('Owner')