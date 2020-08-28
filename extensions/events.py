import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = self.bot.get_channel(self.bot.settings.welcome_channel)
        if welcome_channel is not None:
            embed = discord.Embed(
                title="User joined",
                description=f"{member.mention} has joined the server. Say hi!",
                color=discord.Color(0x00ff00),
                )
            embed.set_footer(text=f"Using Discord since {member.created_at.date()}")
            embed.set_thumbnail(url=member.avatar_url)
            await welcome_channel.send(embed=embed)
        autoroles = []
        for role_id in self.bot.settings.autoroles:
            role = member.guild.get_role(role_id)
            if role:
                autoroles.append(role)
        if autoroles:
            await member.add_roles(*autoroles)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        welcome_channel = self.bot.get_channel(self.bot.settings.welcome_channel)
        if welcome_channel is not None:
            await welcome_channel.send(embed=discord.Embed(
                title="User left",
                description=f"{member} has left the server. See you next time!",
                color=discord.Color(0xff0000))
                .set_thumbnail(url=member.avatar_url),
                )


# Load extension
def setup(bot):
    bot.add_cog(Events(bot))


# Unload extension
def teardown(bot):
    bot.remove_cog("Events")
