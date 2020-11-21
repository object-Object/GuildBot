import re
from typing import Optional

import discord
from discord.ext import commands

from utils import checks, converters, errors


async def user_can_edit_thread(bot, user, channel):
    role = channel.guild.get_role((await bot.database.get_settings(channel.guild.id))["trustee_role"])
    thread_author_id = await bot.database.get_author_of_thread(channel.id)
    if thread_author_id is not None and user.id != thread_author_id and role not in user.roles:
        raise errors.NotThreadAuthor()
    return True


async def raise_bad_category(ctx):
    category_names = []
    for category in await ctx.bot.database.get_thread_categories(ctx.guild.id):
        try:
            category_names.append(ctx.guild.get_channel(category["category_id"]).name)
        except AttributeError:
            pass
    raise commands.BadArgument(f"category must be one of the following: `{'`, `'.join(category_names)}`.")


class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def channel_is_thread():
        async def predicate(ctx):
            if await ctx.bot.database.get_thread(ctx.channel.id) is None:
                raise errors.ThreadOnly()
            return True
        return commands.check(predicate)

    def author_can_archive():
        # Raises an error if the user isn't the thread author, or a Trustee.
        # Should be used with channel_is_thread for checking if thread
        async def predicate(ctx):
            return await user_can_edit_thread(ctx.bot, ctx.author, ctx.channel)
        return commands.check(predicate)

    @commands.command(
        brief="Starts a new thread.",
        help="If the title or category contains spaces it must be put in quotes. The content should not be put into quotes.",
        )
    @commands.guild_only()
    async def thread(self, ctx, category: converters.CategoryConverter, title, *, content):
        if category.id not in [category_id["category_id"] for category_id in await ctx.bot.database.get_thread_categories(ctx.guild.id)]:
            await raise_bad_category(ctx)
        if not ctx.author.permissions_in(category).view_channel:
            raise commands.MissingPermissions(["view_channel"])
        if len(title) > 256:
            raise(commands.BadArgument("Title must not be longer than 256 characters."))

        channel_name = re.sub(r"\s+", "-", title.lower())  # replace spaces with a single dash
        channel_name = re.sub(r"[^a-zA-Z0-9_\-]", "", channel_name)  # remove any illegal characters as defined by Discord
        channel_name = re.sub(r"\-+", "-", channel_name)  # collapse multiple dashes into a single dash
        channel_name = re.sub(r"^\-", "", channel_name)  # remove leading dashes
        channel_name = re.sub(r"\-$", "", channel_name)  # remove trailing dashes
        if len(channel_name) > 999 or len(channel_name) < 1:
            raise commands.BadArgument("Title must be 1-999 characters after being formatted into a valid channel name.")

        channel = await category.create_text_channel(channel_name, topic=f"Thread started by {ctx.author.mention}.")
        message = await channel.send(embed=discord.Embed(
            title=title,
            description=content,
            color=discord.Color(0x007fff)).set_footer(
                text=f"Thread started by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url,
            ))
        await message.pin()
        await ctx.send(embed=discord.Embed(
            title="Thread started",
            description=f"A new thread has been started in {channel.mention} by {ctx.author.mention}.",
            color=discord.Color(0x007fff)))

        await self.bot.database.create_thread(channel.id, ctx.author.id, category.id)

    @thread.error
    async def thread_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                # replace Channel with Category in default error message for clarity
                description=re.sub(r"^Channel", "Category", str(error)),
                color=discord.Color(0xff0000)))

    @commands.command(
        brief="Archives the channel it is used in.",
        help="Must be used in a channel that was created using the `thread` command.",
        )
    @commands.guild_only()
    @channel_is_thread()
    @author_can_archive()
    async def archive(self, ctx, *, reason):
        category = ctx.guild.get_channel((await ctx.bot.database.get_settings(ctx.guild.id))["archive_category"])
        if category is None:
            raise errors.GuildMissingCategory("Archive category not found.")
        if ctx.channel.category.id == category:
            return

        await ctx.send(embed=discord.Embed(
            title="Thread archived",
            description=reason,
            color=discord.Color(0x007fff)).set_footer(
                text=f"Thread archived by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url))

        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.update(
            send_messages=False,
            manage_messages=False,
            add_reactions=False,
            manage_channels=False)
        await ctx.channel.edit(category=category, overwrites={ctx.guild.default_role: overwrite})

    @commands.command(
        brief="Necroes (un-archives) the specified channel.",
        help="The specified channel must have been created using the `thread` command.",
        aliases=["unarchive", "un-archive"],
        )
    @commands.guild_only()
    async def necro(self, ctx, channel: converters.ThreadConverter, *, reason):
        if not ctx.author.permissions_in(channel).view_channel:
            raise commands.MissingPermissions(["view_channel"])
        await user_can_edit_thread(ctx.bot, ctx.author, channel)  # will raise an exception if they can't edit the thread
        if channel.category.id != (await self.bot.database.get_settings(ctx.guild.id))["archive_category"]:
            raise commands.BadArgument(f"{channel.mention} is not archived.")

        category = ctx.guild.get_channel(await self.bot.database.get_category_of_thread(channel.id))

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.update(
            send_messages=None,
            manage_messages=None,
            add_reactions=None,
            manage_channels=None)
        await channel.edit(category=category, overwrites={ctx.guild.default_role: overwrite})

        await channel.send(embed=discord.Embed(
            title="Thread necroed",
            description=reason,
            color=discord.Color(0x007fff)).set_footer(
                text=f"Thread necroed by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url))

        await ctx.send(embed=discord.Embed(
            title="Thread necroed",
            description=f"The thread {channel.mention} has been necroed by {ctx.author.mention}.",
            color=discord.Color(0x007fff)))

    @commands.command(name="import", brief="Imports a channel to the thread system. This cannot be undone.")
    @commands.guild_only()
    @checks.trustee_only()
    async def cmd_import(self, ctx, channel: converters.TextChannelConverter,
                         category: Optional[converters.CategoryConverter]):
        if await ctx.bot.database.get_thread(channel.id):
            raise commands.BadArgument(f"{channel.mention} is already a thread.")

        channel_is_archived = channel.category.id == (await ctx.bot.database.get_settings(ctx.guild.id))["archive_category"]
        thread_categories = await ctx.bot.database.get_thread_categories(ctx.guild.id)

        if category is None:
            if channel_is_archived:
                raise commands.BadArgument(f"{channel.mention} is archived, so a valid category must be specified as an argument.")
            category = channel.category
        if category.id not in [category_id["category_id"] for category_id in thread_categories]:
            await raise_bad_category(ctx)

        if channel_is_archived:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.update(
                send_messages=False,
                manage_messages=False,
                add_reactions=False,
                manage_channels=False)
            await channel.edit(overwrites={ctx.guild.default_role: overwrite})
        else:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.update(
                send_messages=None,
                manage_messages=None,
                add_reactions=None,
                manage_channels=None)
            await channel.edit(category=category, overwrites={ctx.guild.default_role: overwrite})  # if the channel isn't already in the chosen category, move it there

        await ctx.bot.database.create_thread(channel.id, ctx.author.id, category.id)

        await ctx.send(embed=discord.Embed(
            title="Thread imported",
            description=f"{channel.mention} has been converted to a thread by {ctx.author.mention}, who has also been set as the thread's author.",
            color=discord.Color(0x007fff)))

    @archive.error
    @necro.error
    async def archive_necro_error(self, ctx, error):
        if isinstance(error, errors.ThreadOnly) or isinstance(error, errors.NotThreadAuthor):
            await ctx.send(embed=discord.Embed(
                title="Command couldn't be run!",
                description=str(error),
                color=discord.Color(0xff0000)))
        elif isinstance(error, errors.GuildMissingCategory):
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=str(error),
                color=discord.Color(0xff0000)))

    @commands.command(aliases=["syncperms"])
    @commands.guild_only()
    @checks.channel_in_category()
    async def syncpermissions(self, ctx):
        if ctx.channel.permissions_synced:
            raise commands.CheckFailure("This channel's permissions are already synced with its category.")
        await ctx.channel.edit(sync_permissions=True)
        await ctx.send(embed=discord.Embed(
            title="Channel permissions synced",
            description="This channel's permissions are now synced with its category.",
            color=discord.Color(0x007fff)))

    @commands.command(brief="Posts the current channel's topic.")
    async def topic(self, ctx):
        embed = discord.Embed(
            title="Channel topic",
            description=ctx.channel.topic or "Topic not set!",
            color=discord.Color(0x007fff) if ctx.channel.topic else discord.Color(0xff0000))
        if ctx.channel.topic:
            embed.set_footer(
                text="Remember to stay on topic!"
                )
        await ctx.send(embed=embed)


# Load extension
def setup(bot):
    bot.add_cog(Channels(bot))
    bot.get_command("thread").handled_errors = (commands.BadArgument,)
    bot.get_command("archive").handled_errors = (
        errors.ThreadOnly,
        errors.NotThreadAuthor,
        errors.GuildMissingCategory,
        )
    bot.get_command("necro").handled_errors = (
        errors.ThreadOnly,
        errors.NotThreadAuthor,
        errors.GuildMissingCategory,
        )


# Unload extension
def teardown(bot):
    bot.remove_cog("Channels")
