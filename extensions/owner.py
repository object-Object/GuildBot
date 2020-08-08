from discord.ext import commands

class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True)
	@commands.is_owner()
	async def extensions(self, ctx):
		prefix = self.bot.command_prefix
		await ctx.send(f"""`{prefix}extensions load <extension>` Loads specified extension
`{prefix}extensions unload <extension>` Unloads specified extension
`{prefix}extensions reload <extension>` Reloads specified extension""")

def setup(bot):
	bot.add_cog(Owner(bot))

def teardown(bot):
	bot.remove_cog('Owner')