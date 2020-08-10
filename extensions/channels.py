import discord
from discord.ext import commands
import config
import re

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class CategoryConverter(commands.Converter):
        async def convert(self, ctx, argument):
            channel = discord.utils.find(lambda c: c.name.lower()==argument.lower(), ctx.guild.categories)
            if not isinstance(channel, discord.CategoryChannel):
                return await commands.CategoryChannelConverter().convert(ctx, argument)
            return channel

    @commands.command(brief="Starts a new thread.", help="If the title or category contain spaces, it must be put into quotes. The content does **not** need to be put into quotes.")
    @commands.guild_only()
    async def thread(self, ctx, title, category: CategoryConverter, *, content):
        if not category.name.lower() in config.allowed_thread_categories:
            raise commands.BadArgument(f"The category's name must be one of `{'`, `'.join(config.allowed_thread_categories)}` (case-insensitive).")
        if not ctx.author.permissions_in(category).view_channel:
            raise commands.MissingPermissions(["view_channel"])
        if len(title)>256:
            raise(commands.BadArgument("title must not be longer than 256 characters."))

        channel_name = re.sub(r"\s+", "-", title.lower())
        channel_name = re.sub(r"[^a-zA-Z0-9_\-]", "", channel_name)
        channel_name = re.sub(r"\-+", "-", channel_name)
        if len(channel_name)>200 or len(channel_name)<2:
            raise commands.BadArgument("title must be 2-200 characters long after being formatted into a valid channel name.")

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

    @thread.error
    async def thread_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(
                title="Command failed!",
                # replacing Channel with Category at the start of the string because the default error message from CategoryChannelConverter is bad
                description=re.sub(r"^Channel", "Category", str(error)),
                color=discord.Color(0xff0000)))

# Load extension
def setup(bot):
    bot.add_cog(Channels(bot))
    bot.get_command("thread").handled_errors=(
        commands.BadArgument,
        )

# Unload extension
def teardown(bot):
    bot.remove_cog("Channels")