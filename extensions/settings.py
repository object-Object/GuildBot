import discord
from discord.ext import commands


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        for setting in self.bot.settings.__dict__.keys():
            if isinstance(self.bot.settings.__dict__[setting], list):
                parent, add, remove = self._build_list_command(setting)
                group = commands.Group(parent, name=setting, brief="Lists current values")
                group.add_command(commands.Command(add, brief="Adds a value"))
                group.add_command(commands.Command(remove, brief="Removes a value"))
                self.settings.add_command(group)
            else:
                command = commands.Command(self._build_command(setting), name=setting, brief=f"Edits the value of {setting}")
                self.settings.add_command(command)

    def _build_list_command(self, attribute):
        async def parent(ctx):
            await ctx.send(embed=discord.Embed(
                title="Current Value",
                description=f"`{attribute}` is currently set to `{getattr(self.bot.settings, attribute)}`.",
                color=discord.Color(0x007fff),
                ))

        async def add(ctx, value=None):
            if not value:
                await ctx.send(embed=discord.Embed(
                    title="Current Value",
                    description=f"`{attribute}` is currently set to `{getattr(self.bot.settings, attribute)}`.",
                    color=discord.Color(0x007fff),
                    ))
            else:
                lis = getattr(self.bot.settings, attribute)
                lis.append(value)
                setattr(self.bot.settings, lis)
                await ctx.send(embed=discord.Embed(
                    title="Added Value",
                    description=f"`{value}` has been added to `{attribute}`.",
                    color=discord.Color(0x007fff),
                    ))

        async def remove(ctx, value=None):
            if not value:
                await ctx.send(embed=discord.Embed(
                    title="Current Value",
                    description=f"`{attribute}` is currently set to `{getattr(self.bot.settings, attribute)}`.",
                    color=discord.Color(0x007fff),
                    ))
            else:
                lis = getattr(self.bot.settings, attribute)
                lis.remove(value)
                setattr(self.bot.settings, lis)
                await ctx.send(embed=discord.Embed(
                    title="Removed Value",
                    description=f"`{value}` has been removed from `{attribute}`.",
                    color=discord.Color(0x007fff),
                    ))
        return parent, add, remove

    def _build_command(self, attribute):
        async def func(ctx, value=None):
            if not value:
                await ctx.send(embed=discord.Embed(
                    title="Current Value",
                    description=f"`{attribute}` is currently set to `{getattr(self.bot.settings, attribute)}`.",
                    color=discord.Color(0x007fff),
                    ))
            else:
                setattr(self.bot.settings, attribute, value)
                await ctx.send(embed=discord.Embed(
                    title="Set Value",
                    description=f"`{attribute}` has been set to `{value}`.",
                    color=discord.Color(0x007fff),
                    ))
        return func

    @commands.group(invoke_without_command=True)
    async def settings(self, ctx):
        embed = discord.Embed(
            title="Settings",
            description="All currently set settings",
            color=discord.Color(0x007fff))

        for attr in self.bot.settings.__dict__.keys():
            embed.add_field(name=attr, value=f"`{self.bot.settings.__dict__[attr]}`")

        await ctx.send(embed=embed)


# Load extension
def setup(bot):
    bot.add_cog(Settings(bot))


# Unload extension
def teardown(bot):
    bot.remove_cog("Settings")
