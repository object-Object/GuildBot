import discord
from discord.ext import commands


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


def setup(bot):
    bot.add_cog(Utilities(bot))


def teardown(bot):
    bot.remove_cog("Utilities")