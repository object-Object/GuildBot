import discord
from discord.ext import commands
from datetime import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = self.bot.get_channel(self.bot.settings.welcome_channel)
        if welcome_channel is not None:
            delta = datetime.now() - member.created_at
            await welcome_channel.send(embed=discord.Embed(
                title="User joined",
                description=f"{member.mention} has joined the server.{''' They're new to Discord.''' if delta.days<=7 else ''} Say hi!",
                color=discord.Color(0x00ff00))
                .set_footer(text=f"Using Discord since {member.created_at.date()}")
                .set_thumbnail(url=member.avatar_url)
                )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        welcome_channel = self.bot.get_channel(self.bot.settings.welcome_channel)
        if welcome_channel is not None:
            await welcome_channel.send(embed=discord.Embed(
                title="User left",
                description=f"{member} has left the server. See you next time!",
                color=discord.Color(0xff0000))
                .set_thumbnail(url=member.avatar_url)
                )

# Load extension
def setup(bot):
    bot.add_cog(Events(bot))

# Unload extension
def teardown(bot):
    bot.remove_cog("Events")