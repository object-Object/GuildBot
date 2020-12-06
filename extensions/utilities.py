import discord
from discord.ext import commands
from utils import checks


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Quotes a message by link or id.")
    async def quote(self, ctx, message: commands.MessageConverter):
        await ctx.send(
            embed=discord.Embed(
                title="Quoted message",
                description=f"{message.content}\n\n[Jump to message]({message.jump_url})",
                timestamp=message.created_at,
                color=discord.Color(0x007fff)).set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar_url
                    ).set_footer(
                    text=f"Files: {len(message.attachments)}  •  Embeds (not quoted): {len(message.embeds)}"
                    ),
            files=[await attachment.to_file() for attachment in message.attachments]
            )

    @commands.guild_only()
    @checks.trustee_only()
    @commands.command(brief="Purges messages from a channel.")
    async def clear(self, ctx, start_message: commands.MessageConverter, end_message: commands.MessageConverter):
        if not (ctx.channel == start_message.channel == end_message.channel):
            raise commands.BadArgument("start_message and end_message must both be in the current channel.")
        if start_message == end_message:
            raise commands.BadArgument("start_message and end_message must not be the same message.")

        # make sure the messages are in the right order, i.e. message1 is earlier than message2
        if start_message.created_at > end_message.created_at:
            message1, message2 = end_message, start_message
        else:
            message1, message2 = start_message, end_message

        async with ctx.channel.typing():
            num_deleted = len(await ctx.channel.purge(before=message2, after=message1))
            await message1.delete()
            await message2.delete()
            num_deleted += 2

        await ctx.send(
            embed=discord.Embed(
                title="Messages cleared",
                description=f"**{num_deleted}** messages have been deleted from this channel.",
                color=discord.Color(0x007fff)))


def setup(bot):
    bot.add_cog(Utilities(bot))


def teardown(bot):
    bot.remove_cog("Utilities")
