import typing

import discord
from discord.ext import commands

from utils import checks, converters, errors

display_lookup = {
    discord.Role: "mention",
    discord.CategoryChannel: "name",
    discord.TextChannel: "mention",
    }


def display(obj):
    for k, v in display_lookup.items():
        if isinstance(obj, k):
            return getattr(obj, v)
    raise Exception(f"Type {type(obj)} not found in display_lookup")


async def set_single_setting(ctx, setting_key, old_obj, new_obj):
    if new_obj is None:
        await ctx.send(embed=discord.Embed(
            title="Current value",
            description=f"`{setting_key}` is currently {display(old_obj) if old_obj else 'not set'}.",
            color=discord.Color(0x007fff)))
    else:
        setattr(ctx.bot.settings, setting_key, new_obj.id)
        ctx.bot.settings.save()
        await ctx.send(embed=discord.Embed(
            title="Updated value",
            description=f"`{setting_key}` has been {f'changed from {display(old_obj)}' if old_obj else 'set'} to {display(new_obj)}.",
            color=discord.Color(0x007fff)))


async def show_list_setting(ctx, setting_key, get_func):
    obj_displays = []
    for obj_id in getattr(ctx.bot.settings, setting_key):
        try:
            obj_displays.append(display(get_func(obj_id)))
        except AttributeError:
            pass
    await ctx.send(embed=discord.Embed(
        title="Current value",
        description=f"The current values of `{setting_key}` are: {', '.join(obj_displays) if obj_displays else '(not set)'}.",
        color=discord.Color(0x007fff)))


async def add_to_list_setting(ctx, setting_key, objs):
    obj_displays = []
    to_add = []
    invalid_obj_displays = []
    setting = getattr(ctx.bot.settings, setting_key)
    for obj in objs:
        if obj.id in setting:
            invalid_obj_displays.append(display(obj))
        else:
            obj_displays.append(display(obj))
            to_add.append(obj.id)
    if invalid_obj_displays:
        await ctx.send(embed=discord.Embed(
            title="Command failed!",
            description=f"The following values were already in `{setting_key}`: {', '.join(invalid_obj_displays)}.",
            color=discord.Color(0xff0000)))
    else:
        setting += to_add
        ctx.bot.settings.save()
        await ctx.send(embed=discord.Embed(
            title="Updated value",
            description=f"The following values have been added to `{setting_key}`: {', '.join(obj_displays)}.",
            color=discord.Color(0x007fff)))


async def remove_from_list_setting(ctx, setting_key, objs):
    obj_displays = []
    to_remove = []
    invalid_obj_displays = []
    setting = getattr(ctx.bot.settings, setting_key)
    for obj in objs:
        if obj.id not in setting:
            invalid_obj_displays.append(display(obj))
        else:
            obj_displays.append(display(obj))
            to_remove.append(obj.id)
    if invalid_obj_displays:
        await ctx.send(embed=discord.Embed(
            title="Command failed!",
            description=f"The following values were not in `{setting_key}`: {', '.join(invalid_obj_displays)}.",
            color=discord.Color(0xff0000)))
    else:
        for obj_id in to_remove:
            setting.remove(obj_id)
        ctx.bot.settings.save()
        await ctx.send(embed=discord.Embed(
            title="Updated value",
            description=f"The following values have been removed from `{setting_key}`: {', '.join(obj_displays)}.",
            color=discord.Color(0x007fff)))


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["trole"])
    @commands.guild_only()
    @checks.is_guild_owner()
    async def trusteerole(self, ctx, new_role: typing.Optional[converters.RoleConverter]):
        old_role = ctx.guild.get_role(ctx.bot.settings.trustee_role)
        if old_role is not None and new_role is not None:
            raise errors.CommandFailed("`trustee_role` cannot be changed once set.")
        await set_single_setting(ctx, "trustee_role", old_role, new_role)

    @commands.command(aliases=["archivecat"])
    @commands.guild_only()
    @checks.trustee_only()
    async def archivecategory(self, ctx, new_category: typing.Optional[converters.CategoryConverter]):
        old_category = ctx.guild.get_channel(ctx.bot.settings.archive_category)
        await set_single_setting(ctx, "archive_category", old_category, new_category)

    @commands.group(aliases=["threadcats"], invoke_without_command=True)
    @commands.guild_only()
    @checks.trustee_only()
    async def threadcategories(self, ctx):
        await show_list_setting(ctx, "thread_categories", ctx.guild.get_channel)

    @threadcategories.command()
    @commands.guild_only()
    @checks.trustee_only()
    async def add(self, ctx, *categories: commands.Greedy[converters.CategoryConverter]):
        if not categories:  # this is needed because varargs by default are fine with having 0 arguments
            raise commands.MissingRequiredArgument(ctx.command.clean_params["categories"])
        await add_to_list_setting(ctx, "thread_categories", categories)

    @threadcategories.command()
    @commands.guild_only()
    @checks.trustee_only()
    async def remove(self, ctx, *categories: commands.Greedy[converters.CategoryConverter]):
        if not categories:  # this is needed because varargs by default are fine with having 0 arguments
            raise commands.MissingRequiredArgument(ctx.command.clean_params["categories"])
        await remove_from_list_setting(ctx, "thread_categories", categories)

    @commands.command(aliases=["welcomechan"])
    @commands.guild_only()
    @checks.trustee_only()
    async def welcomechannel(self, ctx, new_channel: typing.Optional[converters.TextChannelConverter]):
        old_channel = ctx.guild.get_channel(ctx.bot.settings.welcome_channel)
        await set_single_setting(ctx, "welcome_channel", old_channel, new_channel)


# Load extension
def setup(bot):
    bot.add_cog(Settings(bot))


# Unload extension
def teardown(bot):
    bot.remove_cog("Settings")
