import discord
from discord.ext import commands
from utils import converters, checks
import typing

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["trole"])
    @commands.guild_only()
    @checks.trustee_only()
    async def trusteerole(self, ctx, role: typing.Optional[converters.RoleConverter]):
        if role is None:
            current_role=ctx.guild.get_role(ctx.bot.settings.trustee_role)
            await ctx.send(embed=discord.Embed(
                title="Current value",
                description=f"The Trustee role is currently {current_role.mention if current_role else 'not set'}.",
                color=discord.Color(0x007fff)))
        else:
            ctx.bot.settings.trustee_role=role.id
            ctx.bot.settings.save()
            await ctx.send(embed=discord.Embed(
                title="Updated value",
                description=f"The Trustee role has been set to {role.mention}.",
                color=discord.Color(0x007fff)))

    @commands.command(aliases=["archivecat"])
    @commands.guild_only()
    @checks.trustee_only()
    async def archivecategory(self, ctx, category: typing.Optional[converters.CategoryConverter]):
        if category is None:
            current_category=ctx.guild.get_channel(ctx.bot.settings.archive_category)
            await ctx.send(embed=discord.Embed(
                title="Current value",
                description=f"The archive category is currently {'`'+current_category.name+'`' if current_category else 'not set'}.",
                color=discord.Color(0x007fff)))
        else:
            ctx.bot.settings.archive_category=category.id
            ctx.bot.settings.save()
            await ctx.send(embed=discord.Embed(
                title="Updated value",
                description=f"The archive category has been set to `{category.name}`.",
                color=discord.Color(0x007fff)))

    @commands.group(aliases=["threadcats"], invoke_without_command=True)
    @commands.guild_only()
    @checks.trustee_only()
    async def threadcategories(self, ctx):
        category_names = []
        for category_id in ctx.bot.settings.thread_categories:
            try:
                category_names.append(ctx.guild.get_channel(category_id).name)
            except AttributeError:
                pass
        await ctx.send(embed=discord.Embed(
            title="Current value",
            description=f"The current thread categories are: {'`'+'`, `'.join(category_names)+'`' if category_names else 'not set'}.",
            color=discord.Color(0x007fff)))

    @threadcategories.command()
    @commands.guild_only()
    @checks.trustee_only()
    async def add(self, ctx, *categories: commands.Greedy[converters.CategoryConverter]):
        category_names = []
        for category in categories:
            category_names.append(category.name)
            ctx.bot.settings.thread_categories.append(category.id)
        ctx.bot.settings.save()
        await ctx.send(embed=discord.Embed(
            title="Updated value",
            description=f"The following have been added to the thread categories: `{'`, `'.join(category_names)}`.",
            color=discord.Color(0x007fff)))

    @threadcategories.command()
    @commands.guild_only()
    @checks.trustee_only()
    async def remove(self, ctx, *categories: commands.Greedy[converters.CategoryConverter]):
        category_names = []
        invalid_category_names = []
        for category in categories:
            try:
                ctx.bot.settings.thread_categories.remove(category.id)
                category_names.append(category.name)
            except ValueError:
                invalid_category_names.append(category.name)
        if invalid_category_names:
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=f"The following were not in the thread categories: `{'`, `'.join(invalid_category_names)}`.",
                color=discord.Color(0xff0000)))
        else:
            ctx.bot.settings.save()
            await ctx.send(embed=discord.Embed(
                title="Updated value",
                description=f"The following have been removed from the thread categories: `{'`, `'.join(category_names)}`.",
                color=discord.Color(0x007fff)))

    @commands.command(aliases=["welcomechan"])
    @commands.guild_only()
    @checks.trustee_only()
    async def welcomechannel(self, ctx, channel: typing.Optional[converters.TextChannelConverter]):
        if channel is None:
            current_channel=ctx.guild.get_channel(ctx.bot.settings.welcome_channel)
            await ctx.send(embed=discord.Embed(
                title="Current value",
                description=f"The welcome channel is currently {current_channel.mention if current_channel else 'not set'}.",
                color=discord.Color(0x007fff)))
        else:
            ctx.bot.settings.welcome_channel=channel.id
            ctx.bot.settings.save()
            await ctx.send(embed=discord.Embed(
                title="Updated value",
                description=f"The welcome channel has been set to {channel.mention}.",
                color=discord.Color(0x007fff)))

# Load extension
def setup(bot):
    bot.add_cog(Settings(bot))

# Unload extension
def teardown(bot):
    bot.remove_cog("Settings")