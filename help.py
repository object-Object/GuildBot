import discord
from discord.ext import commands

class GuildBotHelp(commands.HelpCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", description="Listing all top-level commands and groups. Specify a command to see more information.", colour=discord.Colour.blue())

        fields = []
        for cog in mapping.keys():
            if cog:
                if len(mapping[cog])>0:
                    name = cog.qualified_name
                else:
                	name = None
            else:
                name = "Uncategorized"
            if name is not None:
            	fields.append((name, f"`{'`, `'.join([command.name for command in mapping[cog]])}`" ))
        fields.sort()
        for field in fields:
            embed.add_field(name=field[0], value=field[1])

        await self.get_destination().send(embed=embed)
    
    async def send_cog_help(self, cog):
        embed = discord.Embed(title=cog.qualified_name, description=cog.description, colour=discord.Colour.blue())

        for command in cog.get_commands():
            embed.add_field(name=command.name, value=command.brief)
        
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.name, description="`{}` - {}".format(self.get_command_signature(group), group.help), colour=discord.Colour.blue())

        for command in group.commands:
            embed.add_field(name=command.name, value=command.brief)
        
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=command.name, description="`{}` - {}".format(self.get_command_signature(command), command.help), colour=discord.Colour.blue())
        
        await self.get_destination().send(embed=embed)