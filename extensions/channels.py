import discord
from discord.ext import commands
import config
import re
from utils import errors

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class CategoryConverter(commands.Converter):
        async def convert(self, ctx, argument):
            channel = discord.utils.find(lambda c: c.name.lower()==argument.lower(), ctx.guild.categories)
            if not isinstance(channel, discord.CategoryChannel):
                return await commands.CategoryChannelConverter().convert(ctx, argument)
            return channel

    def channel_is_thread():
        async def predicate(ctx):
            conn = ctx.bot.conn
            c = conn.cursor()
            c.execute("SELECT * FROM threads WHERE channel_id = ?", (ctx.channel.id,))
            if c.fetchone() is None:
                raise errors.ThreadOnly(f"This command may only be used in a channel that was created using the `{ctx.bot.command_prefix}thread` command.")
            return True
        return commands.check(predicate)

    def author_can_archive():
        # Only raises an error if the user isn't the thread author and doesn't have the Trustee role. If you want an error message for not being in a thread, also use channel_is_thread.
        async def predicate(ctx):
            conn = ctx.bot.conn
            c = conn.cursor()
            c.execute("SELECT author_id FROM threads WHERE channel_id = ?", (ctx.channel.id,))
            role = discord.utils.find(lambda r: r.name==config.trustee_role, ctx.author.roles)
            row = c.fetchone()
            if row is not None and ctx.author.id!=row[0] and role is None:
                raise errors.NotThreadAuthor(f"This command may only be used by someone with the `{config.trustee_role}` role or the user who started the thread.")
            return True
        return commands.check(predicate)

    @commands.command(brief="Starts a new thread.", help="If the title or category contain spaces, it must be put into quotes. The content does **not** need to be put into quotes.")
    @commands.guild_only()
    async def thread(self, ctx, title, category: CategoryConverter, *, content):
        if not category.name.lower() in config.allowed_thread_categories:
            raise commands.BadArgument(f"The category's name must be one of `{'`, `'.join(config.allowed_thread_categories)}` (case-insensitive).")
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

        conn = self.bot.conn
        c = conn.cursor()
        c.execute("INSERT INTO threads VALUES (?, ?)", (channel.id, ctx.author.id))
        conn.commit()

    @thread.error
    async def thread_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                # replacing Channel with Category at the start of the string because the default error message from CategoryChannelConverter is bad
                description=re.sub(r"^Channel", "Category", str(error)),
                color=discord.Color(0xff0000)))

    @commands.command(brief="Archives the channel it is used in. Can only be used in a thread.")
    @commands.guild_only()
    @channel_is_thread()
    @author_can_archive()
    async def archive(self, ctx, *, reason):
        category = discord.utils.find(lambda c: c.name.lower()==config.archive_category.lower(), ctx.guild.categories)
        if category is None:
            raise errors.GuildMissingCategory(f'Category "{config.archive_category}" not found.')

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

    @commands.command(brief="Necroes (un-archives) the channel it is used in. Can only be used in a thread.", aliases=["unarchive", "un-archive"])
    @commands.guild_only()
    @channel_is_thread()
    @author_can_archive()
    async def necro(self, ctx, category: CategoryConverter, *, reason):
        if not category.name.lower() in config.allowed_thread_categories:
            raise commands.BadArgument(f"The category's name must be one of `{'`, `'.join(config.allowed_thread_categories)}` (case-insensitive).")
        if not ctx.author.permissions_in(category).view_channel:
            raise commands.MissingPermissions(["view_channel"])

        await ctx.send(embed=discord.Embed(
            title="Thread necroed",
            description=reason,
            color=discord.Color(0x007fff)).set_footer(
                text=f"Thread necroed by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url))

        overwrites={ctx.guild.default_role: discord.PermissionOverwrite(
            send_messages=None,
            manage_messages=None,
            add_reactions=None,
            manage_channels=None)}
        await ctx.channel.edit(
            category=category,
            overwrites=overwrites)

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

# Load extension
def setup(bot):
    bot.add_cog(Channels(bot))
    bot.get_command("thread").handled_errors=(commands.BadArgument,)
    bot.get_command("archive").handled_errors=(
        errors.ThreadOnly,
        errors.NotThreadAuthor,
        errors.GuildMissingCategory
        )

# Unload extension
def teardown(bot):
    bot.remove_cog("Channels")