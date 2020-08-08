# Template Cog
Following is an template used to create new cogs.

    from discord.ext import commands

    class Template(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        // How to do events
        @commands.Cog.listener()
        async def on_message(self, message):
            print(message.content)
        
        // How to do commands in cogs
        @commands.command()
        async def message(self, ctx):
            ctx.send("...")

    // Load extension
    def setup(bot):
        bot.add_cog(Template(bot))

    // Unload extension
    def teardown(bot):
        bot.remove_cog('Template')

This should be copied into a new file under the extensions folder. It will automatically be added during launch.
And can be loaded without any further setup during runtime using load command.
