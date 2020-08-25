import discord
from discord.ext import commands
import config
import re
from utils import errors, converters

async def user_can_edit_thread(bot, user, channel):
    role = channel.guild.get_role(bot.settings.trustee_role)
    thread_author_id = await bot.database.get_author_of_thread(channel.id)
    if thread_author_id is not None and user.id!=thread_author_id and not role in user.roles:
        raise errors.NotThreadAuthor(f"This command may only be used by someone with the Trustee role or the user who started the thread.")
    return True

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def channel_is_thread():
        async def predicate(ctx):
            if await ctx.bot.database.get_thread(ctx.channel.id) is None:
                raise errors.ThreadOnly(f"This command may only be used in a channel that was created using the `{ctx.bot.command_prefix}thread` command.")
            return True
        return commands.check(predicate)

    def author_can_archive():
        # Only raises an error if the user isn't the thread author and doesn't have the Trustee role. If you want an error message for not being in a thread, also use channel_is_thread.
        async def predicate(ctx):
            return await user_can_edit_thread(ctx.bot, ctx.author, ctx.channel)
        return commands.check(predicate)

    @commands.command(brief="Starts a new thread.", help="If the title or category contain spaces, it must be put into quotes. The content does **not** need to be put into quotes.")
    @commands.guild_only()
    async def thread(self, ctx, category: converters.CategoryConverter, title, *, content):
        if not category.id in ctx.bot.settings.thread_categories:
            category_names = []
            for category_id in ctx.bot.settings.thread_categories:
                try:
                    category_names.append(ctx.guild.get_channel(category_id).name)
                except AttributeError:
                    pass
            raise commands.BadArgument(f"category must be one of the following: `{'`, `'.join(category_names)}`.")
        if not ctx.author.permissions_in(category).view_channel:
            raise commands.MissingPermissions(["view_channel"])
        if len(title)>256:
            raise(commands.BadArgument("title must not be longer than 256 characters."))

        channel_name = re.sub(r"\s+", "-", title.lower())  # replace spaces with a single dash
        channel_name = re.sub(r"[^a-zA-Z0-9_\-]", "", channel_name)  # remove any illegal characters as defined by Discord
        channel_name = re.sub(r"\-+", "-", channel_name)  # collapse multiple dashes into a single dash
        channel_name = re.sub(r"^\-", "", channel_name)  # remove leading dashes
        channel_name = re.sub(r"\-$", "", channel_name)  # remove trailing dashes
        if len(channel_name)>999 or len(channel_name)<1:
            raise commands.BadArgument("title must be 1-999 characters long after being formatted into a valid channel name.")

        channel = await category.create_text_channel(channel_name, topic=f"Thread started by {ctx.author.mention}.")
        message = await channel.send(embed=discord.Embed(
            title=title,
            description=content,
            color=discord.Color(0x007fff)).set_footer(
                text=f"Thread started by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url
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
                # replacing Channel with Category at the start of the string because the default error message from CategoryChannelConverter is bad
                description=re.sub(r"^Channel", "Category", str(error)),
                color=discord.Color(0xff0000)))

    @commands.command(brief="Archives the channel it is used in.", help="Must be used in a channel that was created using the `thread` command.", )
    @commands.guild_only()
    @channel_is_thread()
    @author_can_archive()
    async def archive(self, ctx, *, reason):
        category = ctx.guild.get_channel(ctx.bot.settings.archive_category)
        if category is None:
            raise errors.GuildMissingCategory(f'Archive category not found.')
        if ctx.channel.category.id==self.bot.settings.archive_category:
            return

        await ctx.send(embed=discord.Embed(
            title="Thread archived",
            description=reason,
            color=discord.Color(0x007fff)).set_footer(
                text=f"Thread archived by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url))

        overwrites={ctx.guild.default_role: discord.PermissionOverwrite(
            send_messages=False,
            manage_messages=False,
            add_reactions=False,
            manage_channels=False)}
        await ctx.channel.edit(
            category=category,
            overwrites=overwrites)

    @commands.command(brief="Necroes (un-archives) the specified channel.", help="The specified channel must have been created using the `thread` command.", aliases=["unarchive", "un-archive"])
    @commands.guild_only()
    async def necro(self, ctx, channel: converters.ThreadConverter, *, reason):
        if not ctx.author.permissions_in(channel).view_channel:
            raise commands.MissingPermissions(["view_channel"])
        await user_can_edit_thread(ctx.bot, ctx.author, channel)  # will raise an exception if they can't edit the thread
        if channel.category.id!=self.bot.settings.archive_category:
            raise commands.BadArgument(f"{channel.mention} is not archived.")

        category = ctx.guild.get_channel(await self.bot.database.get_category_of_thread(channel.id))

        overwrites={ctx.guild.default_role: discord.PermissionOverwrite(
            send_messages=None,
            manage_messages=None,
            add_reactions=None,
            manage_channels=None)}
        await channel.edit(
            category=category,
            overwrites=overwrites)

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
        elif isinstance(error, commands.BadArgument):  # actually only used for necro
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                description=str(error),
                color=discord.Color(0xff0000)))

# Load extension
def setup(bot):
    bot.add_cog(Channels(bot))
    bot.get_command("thread").handled_errors=(commands.BadArgument,)
    bot.get_command("archive").handled_errors=(
        errors.ThreadOnly,
        errors.NotThreadAuthor,
        errors.GuildMissingCategory,
        )
    bot.get_command("necro").handled_errors=(
        errors.ThreadOnly,
        errors.NotThreadAuthor,
        errors.GuildMissingCategory,
        commands.BadArgument,
        )

# Unload extension
def teardown(bot):
    bot.remove_cog("Channels")
